from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Transcription
from datetime import datetime
import whisperx
import uuid
import os
import json


app = Flask(__name__)
UPLOAD_FOLDER = "static/audio"
TRANSCRIPT_FOLDER = "static/transcripts"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcriptions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

model = None  # модель загружается при первом запросе

@app.route('/')
@app.route('/upload')
def upload():
    return render_template("upload.html")

@app.route('/process', methods=['POST'])
def process():
    global model

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    ext = file.filename.rsplit('.', 1)[-1]
    session_id = str(uuid.uuid4())
    audio_path = f"{UPLOAD_FOLDER}/{session_id}.{ext}"
    file.save(audio_path)

    if model is None:
        print(">>> Загружаем модель whisperx...")
        model = whisperx.load_model("small", device="cpu", compute_type="float32")

    result = model.transcribe(audio_path)
    segments = result["segments"]
    transcript = [{"text": seg["text"], "start": seg["start"], "end": seg["end"]} for seg in segments]

    with open(f"{TRANSCRIPT_FOLDER}/{session_id}.json", "w") as f:
        json.dump(transcript, f)

    duration = round(transcript[-1]['end'], 2) if transcript else 0
    new_entry = Transcription(
        session_id=session_id,
        filename=f"{session_id}.{ext}",
        language=result.get("language", "en"),
        duration=duration
    )
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"session_id": session_id})

@app.route('/result/<session_id>')
def result(session_id):
    audio_url = f"/static/audio/{session_id}.mp3"
    transcript_path = f"{TRANSCRIPT_FOLDER}/{session_id}.json"
    with open(transcript_path, "r") as f:
        transcript = json.load(f)
    return render_template("result.html", audio_url=audio_url, transcript=transcript)

# @app.route("/history")
# def history():
#     records = []
#     for file in os.listdir(TRANSCRIPT_FOLDER):
#         if file.endswith(".json"):
#             session_id = file.rsplit('.', 1)[0]
#             audio_file = next((f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(session_id)), None)
#             if not audio_file:
#                 continue
#             with open(os.path.join(TRANSCRIPT_FOLDER, file)) as f:
#                 transcript = json.load(f)
#             date = datetime.fromtimestamp(os.path.getctime(os.path.join(TRANSCRIPT_FOLDER, file))).strftime('%Y-%m-%d')
#             records.append({
#                 "filename": audio_file,
#                 "language": "en",  # можно улучшить позже
#                 "duration": round(transcript[-1]['end'], 2) if transcript else 0,
#                 "date": date,
#                 "session_id": session_id
#             })
#     return render_template("history.html", history=sorted(records, key=lambda x: x['date'], reverse=True))

@app.route("/history")
def history():
    records = Transcription.query.order_by(Transcription.created_at.desc()).all()
    return render_template("history.html", history=records)

if __name__ == '__main__':
    app.run(debug=True)
