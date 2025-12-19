from fastapi import FastAPI, UploadFile, File, HTTPException
from app.utils import extract_audio, transcribe_audio
from app.processor import TextNotesProcessor
import os
from dotenv import load_dotenv

# Load environment variables (API Keys)
load_dotenv() 

app = FastAPI()

# Initialize the Groq/Pegasus Processor
# Ensure GROQ_API_KEY is in your .env file
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("Warning: GROQ_API_KEY not found in environment variables.")

# Initialize the processor once at startup
# We use try/except block in case of initialization errors
try:
    processor = TextNotesProcessor(groq_api_key=groq_api_key, use_pegasus=True)
except Exception as e:
    print(f"Failed to initialize TextNotesProcessor: {e}")
    processor = None

@app.get("/")
def home():
    return {"message": "Video-to-Summary API is running!"}

@app.post("/summarize_video")
async def summarize_video(video: UploadFile = File(...)):
    if not processor:
        raise HTTPException(status_code=500, detail="Text Processor not initialized properly.")

    try:
        print(f"Processing video: {video.filename}")

        # Step 1: Extract & Transcribe
        audio_path = extract_audio(video)
        transcribed_text = transcribe_audio(audio_path)

        # Step 2: Run full text processing + save JSON
        output_json_path = f"outputs/{video.filename}.json"
        os.makedirs("outputs", exist_ok=True)

        summary_result = processor.process_text(
            raw_text=transcribed_text,
            output_json_path=output_json_path,
            api_delay=1.0,
            generate_mindmap=True  # 🔥 THIS IS IMPORTANT
        )

        # Step 3: Generate mindmap file path
        mindmap_path = output_json_path.replace(".json", "_mindmap.mmd")

        return {
            "status": "success",
            "summary": summary_result,
            "mindmap_file": mindmap_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
