# 🎥 AI Lecture(Video) Summarizer & Mindmap Generator

An intelligent application that takes video input, transcribes the audio, and generates structured summaries and visual mindmaps using advanced AI models.


##Technology Stack Overview and features
* **Transcription**: OpenAI Whisper (Local Execution)
Whisper is used to convert extracted audio into accurate text transcripts. It performs well in noisy environments and supports multiple accents and speaking styles. Running locally ensures data privacy and eliminates dependency on external APIs.

* **Summarization**: Google PEGASUS (Abstractive Summarization)
PEGASUS is used to generate concise and meaningful summaries from long transcripts. It performs abstractive summarization, allowing it to rephrase and compress content instead of copying sentences. This makes summaries more coherent and student-friendly.
* **Intelligence**: Groq LLaMA 3 (Entity Extraction & Logical Analysis)
LLaMA 3 is used for semantic understanding, entity extraction, and logical relationship analysis. It helps identify key concepts, topics, and connections within the summarized content. This enables structured knowledge representation and advanced reasoning.

* **Visualization**: Automated Mermaid.js Mindmaps
Mermaid.js is used to automatically generate mindmaps and diagrams from processed data. It visually represents relationships between topics, making complex information easier to understand. This enhances learning through graphical knowledge organization.

* **Containerization**: Fully Dockerized Setup
The entire system is containerized using Docker for consistent deployment across environments. This ensures dependency isolation, easy setup, and scalability. Docker also simplifies maintenance and collaborative development.

## Tech Stack
* **Backend:** FastAPI (Python)
* **AI Models:** Whisper, Pegasus-XSUM, SentenceTransformers
* **Infrastructure:** Docker & Docker Compose

## Advantages
*Groq is free for students providing better accuracy and extraction compared to the other model given the cost.
*The system runs locally and is fully containerized, ensuring data privacy and eliminating dependency on external cloud services.
*The modular pipeline architecture allows easy upgrades and maintenance without affecting the entire system.

## How to Run
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



## Live Demo Link : 
* https://drive.google.com/file/d/1iPvZAOjkwKe7nG41fRxk0HdRTTYk52Fe/view?usp=sharing
