from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.utils import extract_audio, transcribe_audio
from app.processor import TextNotesProcessor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv() 

app = FastAPI()

# 1. CORS - Crucial for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Initialize Processor
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("Warning: GROQ_API_KEY not found.")

try:
    # We use the new lightweight processor
    processor = TextNotesProcessor(groq_api_key=groq_api_key)
except Exception as e:
    print(f"Failed to initialize TextNotesProcessor: {e}")
    processor = None

# 3. Custom Startup Log
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print("Server running on : http://localhost:8000")
    print("="*50 + "\n")

@app.get("/")
def home():
    return {"message": "Video-to-Summary API is running!"}

@app.post("/summarize_video")
async def summarize_video(video: UploadFile = File(...)):
    if not processor:
        raise HTTPException(status_code=500, detail="Text Processor not initialized.")

    try:
        print(f"Processing video: {video.filename}")

        # Step 1: Extract & Transcribe (Using Groq Whisper now)
        audio_path = extract_audio(video)
        transcribed_text = transcribe_audio(audio_path)

        # Step 2: Processing
        output_json_path = f"outputs/{video.filename}.json"
        os.makedirs("outputs", exist_ok=True)

        # We pass generate_mindmap=True to keep feature parity
        summary_result = processor.process_text(
            raw_text=transcribed_text,
            output_json_path=output_json_path,
            generate_mindmap=True
        )

       # Step 3: Mindmap Path (Frontend expects this)
        mindmap_path = output_json_path.replace(".json", "_mindmap.mmd")

        # --- ADD THIS MISSING BLOCK ---
        mindmap_code = ""
        if os.path.exists(mindmap_path):
            with open(mindmap_path, "r", encoding="utf-8") as f:
                mindmap_code = f.read()
        # ------------------------------

        return {
            "status": "success",
            "summary": summary_result,
            "mindmap_file": mindmap_path,
            "mindmap_code": mindmap_code  # Now this variable exists!
        }
    

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))