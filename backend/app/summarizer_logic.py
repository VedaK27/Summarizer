import json
import re
from groq import Groq

# Large model is preferred for better reasoning & extraction
MODEL_ID = "llama-3.3-70b-versatile"


def initialize_groq_client(api_key):
    # Initialize Groq client using provided API key
    try:
        return Groq(api_key=api_key)
    except Exception:
        return None


def keyword_summarize(text, keyword, api_key):
    """
    Extract and summarize ONLY keyword-related information from text.
    Output is structured so it can be reused for JSON storage or mindmaps.
    """

    # Basic input validation
    if not text or not keyword:
        return {"error": "Text and keyword are required"}

    client = initialize_groq_client(api_key)
    if not client:
        return {"error": "Invalid Groq API configuration"}

    # System instruction focuses strictly on keyword extraction
    system_prompt = (
        "You are a precise information extraction assistant.\n"
        f"Your task is to extract and summarize ONLY the information related to "
        f"the topic '{keyword}'.\n"
        "- Ignore all unrelated content\n"
        "- Do not add new information\n"
        "- If the topic is not mentioned, say:\n"
        "'No relevant information found for this topic.'"
    )

    # User prompt enforces structured output
    user_prompt = f"""
Return ONLY valid JSON with the following fields:
- topic
- summary
- key_points
- related_concepts

Text:
{text}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=700
        )

        raw_output = response.choices[0].message.content.strip()

        # Clean up accidental markdown formatting if any
        raw_output = re.sub(r"^```json|```$", "", raw_output).strip()

        return safe_json_parse(raw_output)

    except Exception as e:
        return {"error": f"Groq API Error: {str(e)}"}


def safe_json_parse(text):
    # Parse JSON safely, fallback if model response is malformed
    try:
        return json.loads(text)
    except Exception:
        return {
            "topic": "Parsing Error",
            "summary": text[:300],
            "key_points": [],
            "related_concepts": []
        }