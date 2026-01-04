import os
import subprocess
from groq import Groq

# Define directories for temporary file storage
UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

def extract_audio(video_file):
    """Saves uploaded video and extracts audio using ffmpeg."""
    video_path = os.path.join(UPLOAD_DIR, video_file.filename)
    audio_path = os.path.join(AUDIO_DIR, video_file.filename + ".wav")

    with open(video_path, "wb") as f:
        f.write(video_file.file.read())

    # Extract audio (keeping 16kHz for compatibility)
    command = f'ffmpeg -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}" -y'
    subprocess.run(command, shell=True)

    return audio_path

def transcribe_audio(audio_path):
    """Transcribes audio file using Groq's Whisper API."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found")

    client = Groq(api_key=api_key)

    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), file.read()),
            model="whisper-large-v3-turbo",  # UPDATED: Replaced deprecated model
            response_format="json",
            temperature=0.0
        )
    
    return transcription.text