import json
import os
import re
import time
from typing import List, Dict
from groq import Groq

class TextNotesProcessor:
    def __init__(self, groq_api_key: str, use_pegasus: bool = False):
        self.client = Groq(api_key=groq_api_key)

    def segment_text(self, text: str, chunk_size: int = 4000) -> List[str]:
        """Simple segmentation by character limit to avoid token overflow."""
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def generate_structured_notes(self, segment: str) -> Dict:
        """Uses Groq to generate the summary and keywords."""
        prompt = f"""Analyze this transcript segment and return valid JSON with these keys:
- topic: Brief title
- summary: Concise summary
- key_points: List of 3-5 bullet points
- keywords: List of 5 keywords

Text: {segment[:3000]}
Return ONLY JSON."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"topic": "Segment", "summary": "", "key_points": [], "keywords": []}

    def generate_mindmap(self, concept: str, output_file: str) -> str:
        """Generates Mermaid.js code using Groq."""
        prompt = f"""Create a Mermaid mindmap for: "{concept}".
Return ONLY the code starting with 'mindmap' and 'root((...))'. No markdown."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            code = response.choices[0].message.content.replace("```mermaid", "").replace("```", "").strip()
            
            with open(output_file, 'w') as f:
                f.write(code)
            return code
        except Exception as e:
            print(f"Mindmap generation failed: {e}")
            return ""

    def process_text(self, raw_text: str, output_json_path: str = None, generate_mindmap: bool = True, **kwargs) -> Dict:
        # 1. Simple processing
        segments = self.segment_text(raw_text)
        structured_segments = [self.generate_structured_notes(seg) for seg in segments]

        # 2. Aggregate Results
        overall_summary = " ".join([s.get('summary', '') for s in structured_segments])
        
        final_output = {
            "overall_summary": overall_summary,
            "segments": structured_segments,
            "metadata": {"pipeline": "Lightweight Groq"}
        }

        # 3. Save JSON
        if output_json_path:
            with open(output_json_path, 'w') as f:
                json.dump(final_output, f, indent=2)

            # 4. Generate Mindmap (Restored for Frontend compatibility)
            if generate_mindmap:
                mindmap_path = output_json_path.replace('.json', '_mindmap.mmd')
                topic_str = ", ".join([s.get('topic', '') for s in structured_segments])
                self.generate_mindmap(f"Summary of: {topic_str}", mindmap_path)

        return final_output