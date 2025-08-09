from flask import Flask, request, send_file, render_template
import whisper
import os
from datetime import datetime

app = Flask(__name__)
model = whisper.load_model("base")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["video"]
        if not file:
            return "No file uploaded", 400
        
        filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        result = model.transcribe(filepath)

        srt_path = filepath + ".srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"]):
                f.write(f"{i+1}\n")
                f.write(f"{format_time(segment['start'])} --> {format_time(segment['end'])}\n")
                f.write(f"{segment['text'].strip()}\n\n")

        return send_file(srt_path, as_attachment=True)

    return render_template("index.html")
