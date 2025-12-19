import os
import subprocess
import whisper

# Define directories for temporary file storage
UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Load the Whisper model once when the module loads
model = whisper.load_model("tiny")

def extract_audio(video_file):
    """Saves uploaded video and extracts audio using ffmpeg."""
    video_path = os.path.join(UPLOAD_DIR, video_file.filename)
    audio_path = os.path.join(AUDIO_DIR, video_file.filename + ".wav")

    with open(video_path, "wb") as f:
        f.write(video_file.file.read())

    # Command from your original utils.py
    command = f'ffmpeg -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}" -y'
    subprocess.run(command, shell=True)

    return audio_path

def transcribe_audio(audio_path):
    """Transcribes audio file to text using Whisper."""
    result = model.transcribe(audio_path)
    return result["text"]