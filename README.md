# 🎥 AI Video Summarizer & Mindmap Generator

An intelligent application that takes video input, transcribes the audio, and generates structured summaries and visual mindmaps using advanced AI models.

## 🚀 Features
* **Transcription:** OpenAI Whisper (running locally).
* **Summarization:** Google Pegasus (Abstractive summarization).
* **Intelligence:** Groq Llama 3 (Entity extraction & Logic).
* **Visualization:** Automated Mermaid.js Mindmaps.
* **Containerization:** Fully Dockerized setup.

## 🛠️ Tech Stack
* **Backend:** FastAPI (Python)
* **AI Models:** Whisper, Pegasus-XSUM, SentenceTransformers
* **Infrastructure:** Docker & Docker Compose

## ⚡ How to Run
1.  Clone the repository.
2.  Create a `.env` file in `backend/` with your API key:
    ```
    GROQ_API_KEY=your_key_here
    ```
3.  Build and run with Docker:
    ```bash
    docker-compose up --build
    ```
4.  Access the API at `http://localhost:8000/docs`.

## ⚠️ Note on Performance
The first build downloads ~3GB of AI models (Pegasus & Whisper). Subsequent starts are instant.