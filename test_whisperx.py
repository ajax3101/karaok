import whisperx

model = whisperx.load_model("small", device="cpu", compute_type="float32")
audio_file = "example.mp3"
result = model.transcribe(audio_file)

print(result["segments"][:2])  # Вывод первых двух сегментов
