import os
from groq import Groq

MODEL_GENERAL = "llama-3.1-8b-instant"
MODEL_LARGE   = "llama-3.3-70b-versatile"

def initialize_groq_client(api_key):
    try:
        return Groq(api_key=api_key)
    except:
        return None

def generate_summary(text, api_key, mode="general", keyword=None):
    client = initialize_groq_client(api_key)
    if not client:
        return "Error: Invalid API Configuration."

    if mode == "keyword" and keyword:
        system_instruction = (
            f"You are a helpful assistant. Extract and summarize only the information related to "
            f"the topic '{keyword}'. Ignore unrelated parts. If the topic isn't present, say so."
        )
        model_id = MODEL_LARGE
    else:
        system_instruction = (
            "You are an expert summarizer. Provide a clear, concise and accurate summary of the text."
        )
        model_id = MODEL_GENERAL

    try:
        resp = client.chat.completions.create(
            messages=[
                {"role":"system", "content": system_instruction},
                {"role":"user",   "content": f"Text:\n\n{text}"}
            ],
            model=model_id,
            temperature=0.4,
            max_tokens=1024
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"
