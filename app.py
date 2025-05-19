from flask import Flask, request, jsonify, render_template, send_from_directory
from models import db, Transcription
from config import Config
import whisperx
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

model = whisperx.load_model("medium.en", device="cpu", compute_type="default")

#@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("audio")
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            try:
                result = model.transcribe(path)
                segments = result.get("segments", [])
                transcript = " ".join([seg.get("text", "") for seg in segments])

                record = Transcription(filename=filename, transcript=transcript)
                record.segments = segments  # можно хранить весь результат
                db.session.add(record)
                db.session.commit()

                return jsonify({"segments": segments})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return jsonify({"error": "No file uploaded"}), 400

    return render_template("index.html")

@app.route("/history")
def history():
    records = Transcription.query.order_by(Transcription.id.desc()).all()
    return jsonify([{"id": r.id, "filename": r.filename} for r in records])

@app.route("/transcription/<int:record_id>")
def transcription(record_id):
    record = Transcription.query.get_or_404(record_id)
    filename = record.filename
    audio_url = f"/uploads/{filename}"
    # Примерные сегменты — нужно будет хранить в БД или json-файле
    segments = record.segments or []
    return jsonify({"audio_url": audio_url, "segments": segments})

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
