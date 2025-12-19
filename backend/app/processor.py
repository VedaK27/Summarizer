import re
import json
import numpy as np
import os
from typing import List, Dict
from groq import Groq
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import time
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

# Disable symlink warning on Windows
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'


# ============================================================================
# TEXT PROCESSING PIPELINE with GROQ API + PEGASUS SUMMARIZATION
# ============================================================================

class TextNotesProcessor:
    """
    Processes raw text (e.g., transcripts) into structured JSON notes
    using spaCy for cleaning, Sentence Transformers for semantic segmentation,
    Groq LLM for structured extraction, and Pegasus for keyword-based summarization.
    """

    def __init__(self, groq_api_key: str, use_pegasus: bool = True):
        """Initialize the processor with Groq API key and NLP models."""
        self.client = Groq(api_key=groq_api_key)

        # Load spaCy for text cleaning
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print(" Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        # Load sentence transformer for segmentation
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Load Pegasus model for summarization
        self.use_pegasus = use_pegasus
        self.pegasus_tokenizer = None
        self.pegasus_model = None

        if self.use_pegasus:
            try:
                print(" Loading Pegasus model for summarization...")
                self.pegasus_model_name = "google/pegasus-xsum"
                self.pegasus_tokenizer = PegasusTokenizer.from_pretrained(self.pegasus_model_name)
                self.pegasus_model = PegasusForConditionalGeneration.from_pretrained(self.pegasus_model_name)
                print("    ✓ Pegasus model loaded successfully")
            except Exception as e:
                print(f"    ⚠ Failed to load Pegasus model: {e}")
                print("    ℹ Installing required dependencies...")
                print("    ℹ Please run: pip install sentencepiece protobuf")
                print("    ℹ Continuing without Pegasus summarization...")
                self.use_pegasus = False

        # Define filler words to remove
        self.filler_words = {
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'sort of',
            'kind of', 'i mean', 'actually', 'basically', 'literally',
            'right', 'okay', 'so', 'well', 'yeah', 'hmm', 'mhm'
        }

    # ------------------------------------------------------------------------
    # STEP 1: DATA CLEANING (spaCy)
    # ------------------------------------------------------------------------

    def clean_text(self, text: str) -> List[str]:
        """Clean transcription: remove fillers, normalize text, and segment into sentences."""
        print("Step 1: Cleaning text with spaCy...")

        doc = self.nlp(text)
        cleaned_sentences = []

        for sent in doc.sents:
            tokens = []

            for token in sent:
                if token.text.lower() in self.filler_words:
                    continue
                if token.is_punct and token.text in [',', '...', '--']:
                    continue
                if token.is_space:
                    continue

                tokens.append(token.text)

            if tokens:
                cleaned = ' '.join(tokens)
                # Remove spaces before punctuation and fix excessive spacing
                cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()

                if cleaned and len(cleaned) > 2:
                    cleaned = cleaned[0].upper() + cleaned[1:]
                    if cleaned[-1] not in '.!?':
                        cleaned += '.'
                    cleaned_sentences.append(cleaned)

        print(f"    Cleaned into {len(cleaned_sentences)} sentences")
        return cleaned_sentences

    # ------------------------------------------------------------------------
    # STEP 2: TOPIC SEGMENTATION (Semantic Similarity)
    # ------------------------------------------------------------------------

    def segment_by_topic(self, sentences: List[str],
                         similarity_threshold: float = 0.5,
                         max_segment_length: int = 500,
                         min_segment_length: int = 100) -> List[str]:
        """Segment sentences into topic blocks using semantic cosine similarity."""
        print("Step 2: Segmenting by topic...")

        if not sentences:
            return []

        embeddings = self.embedding_model.encode(sentences)
        segments = []
        current_segment = [sentences[0]]
        current_word_count = len(sentences[0].split())

        for i in range(1, len(sentences)):
            sentence_word_count = len(sentences[i].split())

            # Force segment break if too long
            if current_word_count + sentence_word_count > max_segment_length:
                segments.append(' '.join(current_segment))
                current_segment = [sentences[i]]
                current_word_count = sentence_word_count
                continue

            similarity = cosine_similarity(
                embeddings[i - 1].reshape(1, -1),
                embeddings[i].reshape(1, -1)
            )[0][0]

            # Break if similarity is below threshold AND segment is large enough
            if similarity < similarity_threshold and current_word_count >= min_segment_length:
                segments.append(' '.join(current_segment))
                current_segment = [sentences[i]]
                current_word_count = sentence_word_count
            else:
                current_segment.append(sentences[i])
                current_word_count += sentence_word_count

        if current_segment:
            segments.append(' '.join(current_segment))

        print(f"    Created {len(segments)} topic segments")
        return segments

    # ------------------------------------------------------------------------
    # NEW: PEGASUS KEYWORD-BASED SUMMARIZATION
    # ------------------------------------------------------------------------

    def generate_pegasus_summary(self, text: str, keywords: List[str] = None,
                                 max_length: int = 150, min_length: int = 50) -> str:
        """
        Generate a summary using Pegasus model, optionally focusing on specific keywords.

        Args:
            text: Input text to summarize
            keywords: Optional list of keywords to emphasize in the summary
            max_length: Maximum length of the summary
            min_length: Minimum length of the summary

        Returns:
            Generated summary string
        """
        if not self.use_pegasus or self.pegasus_model is None or self.pegasus_tokenizer is None:
            return ""

        try:
            # If keywords are provided, prepend them to guide the summarization
            if keywords:
                keyword_prompt = f"Keywords: {', '.join(keywords[:5])}. "
                input_text = keyword_prompt + text
            else:
                input_text = text

            # Tokenize and generate summary
            tokens = self.pegasus_tokenizer(input_text, truncation=True, padding="longest",
                                            return_tensors="pt", max_length=1024)

            summary_ids = self.pegasus_model.generate(
                tokens["input_ids"],
                max_length=max_length,
                min_length=min_length,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )

            summary = self.pegasus_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary.strip()

        except Exception as e:
            print(f"    Pegasus summarization error: {e}")
            return ""

    # ------------------------------------------------------------------------
    # STEP 3: STRUCTURED GENERATION (Groq API) - ENHANCED
    # ------------------------------------------------------------------------

    def generate_structured_notes(self, segment: str) -> Dict:
        """Use Groq LLM to extract structured information from a text segment."""
        prompt = f"""Extract structured information from this text and return ONLY valid JSON with these keys:
- topic: Brief title (5-8 words)
- summary: Concise summary (2-3 sentences)
- key_points: List of 3-5 main points
- action_items: List of tasks/action items (empty list if none)
- questions: List of questions raised (empty list if none)
- keywords: List of 5-8 important keywords

Text: {segment}

Return only JSON, no markdown:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = re.sub(r'^```json?\n|```$', '', result_text, flags=re.MULTILINE).strip()

            data = json.loads(result_text)

            # Generate Pegasus summary if enabled
            pegasus_summary = ""
            if self.use_pegasus:
                keywords = data.get("keywords", [])
                pegasus_summary = self.generate_pegasus_summary(segment, keywords)

            # Ensure all required fields exist
            structured_data = {
                "topic": data.get("topic", "Unknown Topic"),
                "summary": data.get("summary", ""),
                "pegasus_summary": pegasus_summary,  # NEW: Keyword-focused summary
                "key_points": data.get("key_points", []),
                "action_items": data.get("action_items", []),
                "questions": data.get("questions", []),
                "keywords": data.get("keywords", [])
            }

            return structured_data

        except json.JSONDecodeError as e:
            print(f"    JSON parsing error: {e}")
            return {
                "topic": "Error parsing segment",
                "summary": segment[:200] + "...",
                "pegasus_summary": "",
                "key_points": [],
                "action_items": [],
                "questions": [],
                "keywords": []
            }
        except Exception as e:
            raise e

    # ------------------------------------------------------------------------
    # GENERATE OVERALL DOCUMENT SUMMARY
    # ------------------------------------------------------------------------

    def generate_overall_summary(self, segments: List[str]) -> Dict:
        """Generate an overall summary of the entire document using Pegasus."""
        if not self.use_pegasus:
            return {"overall_summary": "Pegasus summarization not enabled"}

        print("\n Generating overall document summary with Pegasus...")

        # Combine all segments (limit to avoid token overflow)
        combined_text = " ".join(segments)[:4000]  # Limit to ~4000 chars

        # Extract keywords from all text first
        doc = self.nlp(combined_text)
        keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 3]
        unique_keywords = list(set(keywords))[:10]  # Top 10 keywords

        # Generate summary
        overall_summary = self.generate_pegasus_summary(
            combined_text,
            unique_keywords,
            max_length=200,
            min_length=80
        )

        print(f"    ✓ Overall summary generated")

        return {
            "overall_summary": overall_summary,
            "document_keywords": unique_keywords
        }

    # ------------------------------------------------------------------------
    # MINDMAP GENERATION (Mermaid)
    # ------------------------------------------------------------------------

    def generate_mindmap(self, concept: str, output_file: str = "mindmap.mmd") -> str:
        """Generate a Mermaid mindmap diagram from a concept using Groq API."""
        print(f"\n Generating mindmap for: {concept}")

        prompt = f"""Create a detailed Mermaid mindmap diagram for the following concept: "{concept}"

Generate a clear, well-structured mindmap using Mermaid syntax. Include:
- Central root node with the main concept
- Multiple branches for key topics/subtopics
- Sub-branches for details and related ideas
- Use proper indentation for hierarchy

Return ONLY the Mermaid code starting with "mindmap" followed by "root((concept))", no explanations or markdown blocks."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            mermaid_code = response.choices[0].message.content.strip()

            # Clean up response
            mermaid_code = re.sub(r'^```mermaid\n?|```$', '', mermaid_code, flags=re.MULTILINE).strip()

            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)

            print(f"    ✓ Mindmap saved to: {output_file}")
            print(f"    ℹ View at: [https://mermaid.live](https://mermaid.live)")

            return mermaid_code

        except Exception as e:
            print(f"     Error generating mindmap: {e}")
            return ""

    def generate_mindmap_from_notes(self, json_file_path: str, output_file: str = "notes_mindmap.mmd") -> str:
        """Generate a high-level mindmap from the structured notes JSON file."""
        print(f"\n Generating mindmap from notes: {json_file_path}")

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f" Error: JSON file not found at {json_file_path}")
            return ""
        except json.JSONDecodeError:
            print(f" Error: Failed to decode JSON from {json_file_path}")
            return ""

        segments = data.get('segments', [])

        # Combine topics into a single concept string for LLM input
        combined_concept = "Session notes covering: " + " | ".join(
            [s.get('topic', f"Segment {s.get('segment_id', '')}") for s in segments])

        return self.generate_mindmap(combined_concept, output_file)

    # ------------------------------------------------------------------------
    # STEP 4: OUTPUT ASSEMBLY
    # ------------------------------------------------------------------------

    def process_all_segments(self, segments: List[str],
                             delay_seconds: float = 0.5) -> Dict:
        """Process all segments and combine into final structured output."""
        print(" Step 3-4: Generating structured notes with Groq + Pegasus...")

        structured_segments = []

        for i, segment in enumerate(segments, 1):
            print(f"    Processing segment {i}/{len(segments)}...")

            retry_count = 0
            max_retries = 3
            success = False

            while retry_count < max_retries and not success:
                try:
                    structured_data = self.generate_structured_notes(segment)
                    structured_data['segment_id'] = i
                    structured_segments.append(structured_data)
                    success = True

                    if i < len(segments):
                        time.sleep(delay_seconds)

                except Exception as e:
                    error_msg = str(e)

                    if "401" in error_msg and "invalid_api_key" in error_msg:
                        print("     CRITICAL ERROR: Invalid Groq API Key (401). Aborting processing.")
                        raise e

                    wait_time = 10 if "429" in error_msg or "rate" in error_msg.lower() else delay_seconds * 2
                    print(
                        f"    ⚠ API error/Rate limit hit. Waiting {wait_time}s... Retrying {retry_count + 1}/{max_retries}")
                    time.sleep(wait_time)
                    retry_count += 1

            if not success:
                print(f"     Failed to process segment {i} after {max_retries} retries")

        # Generate overall document summary
        overall_summary_data = self.generate_overall_summary(segments)

        # Assemble final output
        final_output = {
            "metadata": {
                "total_segments": len(structured_segments),
                "processing_pipeline": "spaCy Clean → Semantic Segment → Groq LLM → Pegasus Summary",
                "model_used": "Groq Llama 3.3 70B + Pegasus-XSUM",
                "pegasus_enabled": self.use_pegasus
            },
            "overall_summary": overall_summary_data.get("overall_summary", ""),
            "document_keywords": overall_summary_data.get("document_keywords", []),
            "segments": structured_segments,
            "all_action_items": self._extract_all_items(structured_segments, "action_items"),
            "all_questions": self._extract_all_items(structured_segments, "questions"),
            "all_keywords": self._extract_unique_keywords(structured_segments)
        }

        print(f"    ✓ Processing complete! ({len(structured_segments)}/{len(segments)} segments)")
        return final_output

    def _extract_all_items(self, segments: List[Dict], key: str) -> List[str]:
        """Extract and flatten a specific list (e.g., action_items) from all segments."""
        items = []
        for seg in segments:
            items.extend(seg.get(key, []))
        return items

    def _extract_unique_keywords(self, segments: List[Dict]) -> List[str]:
        """Extract unique keywords from all segments."""
        keywords = set()
        for seg in segments:
            keywords.update(seg.get('keywords', []))
        return sorted(list(keywords))

    # ------------------------------------------------------------------------
    # MAIN PIPELINE
    # ------------------------------------------------------------------------

    def process_text(self, raw_text: str, output_json_path: str = None,
                     max_segment_length: int = 500,
                     min_segment_length: int = 100,
                     similarity_threshold: float = 0.5,
                     api_delay: float = 0.5,
                     generate_mindmap: bool = False) -> Dict:
        """Complete pipeline: raw text → structured notes JSON."""
        print("\n" + "=" * 70)
        print(" TEXT NOTES PROCESSING PIPELINE (Groq API + Pegasus)")
        print("=" * 70 + "\n")

        # Step 1-2: Preprocessing
        cleaned_sentences = self.clean_text(raw_text)
        segments = self.segment_by_topic(
            cleaned_sentences,
            similarity_threshold=similarity_threshold,
            max_segment_length=max_segment_length,
            min_segment_length=min_segment_length
        )

        # Show estimates
        total_words = sum(len(seg.split()) for seg in segments)
        print(f"\n Processing Info:")
        print(f"    Segments: {len(segments)}")
        print(f"    Avg words/segment: {total_words // len(segments) if segments else 0}")
        print(f"    Est. time: ~{int(len(segments) * api_delay)} seconds\n")

        # Step 3-4: Intelligence & Generation
        final_output = self.process_all_segments(segments, delay_seconds=api_delay)

        # Save to file if requested
        if output_json_path:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)
            print(f"\n Saved output to: {output_json_path}")

            # Generate mindmap if requested
            if generate_mindmap:
                mindmap_path = output_json_path.replace('.json', '_mindmap.mmd')
                self.generate_mindmap_from_notes(output_json_path, mindmap_path)

        return final_output

    def process_text_file(self, text_file_path: str,
                          output_json_path: str = None,
                          max_segment_length: int = 500,
                          min_segment_length: int = 100,
                          similarity_threshold: float = 0.5,
                          api_delay: float = 0.5,
                          generate_mindmap: bool = False) -> Dict:
        """Process text from a file, triggering the main pipeline."""
        print(f" Reading text from: {text_file_path}")
        with open(text_file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        return self.process_text(
            raw_text, output_json_path,
            max_segment_length, min_segment_length,
            similarity_threshold, api_delay, generate_mindmap
        )

    # ------------------------------------------------------------------------
    # FINAL REPORT GENERATION - ENHANCED WITH PEGASUS SUMMARIES
    # ------------------------------------------------------------------------

    def generate_final_report(self, json_file_path: str):
        """
        Reads the structured JSON file and prints the consolidated summary
        and key points in a human-readable format, including Pegasus summaries.
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f" Error: JSON file not found at {json_file_path}")
            return
        except json.JSONDecodeError:
            print(f" Error: Failed to decode JSON from {json_file_path}. File might be corrupted.")
            return

        segments = data.get('segments', [])

        # Print overall summary first (if available)
        print("\n" + "=" * 70)
        print(" CONSOLIDATED FINAL REPORT WITH PEGASUS SUMMARIES")
        print("=" * 70 + "\n")

        if 'overall_summary' in data and data['overall_summary']:
            print("##  Overall Document Summary (Pegasus)")
            print("\n" + data['overall_summary'].strip())
            print("\n" + "---" + "\n")

        # 1. Consolidate LLM Summary
        consolidated_summary_text = " ".join([seg.get('summary', '') for seg in segments if seg.get('summary')])

        print("##  Consolidated Session Summary (Groq LLM)")
        print("\n" + consolidated_summary_text.strip())

        # 2. Print Pegasus summaries for each segment
        print("\n" + "---" + "\n")
        print("##  Keyword-Focused Summaries per Segment (Pegasus)")
        for seg in segments:
            if seg.get('pegasus_summary'):
                print(f"\n**Segment {seg.get('segment_id')}: {seg.get('topic')}**")
                print(f"{seg.get('pegasus_summary')}")

        # 3. Consolidate Key Points (Unique)
        all_key_points = set()
        for seg in segments:
            all_key_points.update(seg.get('key_points', []))

        sorted_key_points = sorted(list(all_key_points))

        print("\n" + "---" + "\n")
        print("##  Key Points (Unique and Consolidated)")
        for point in sorted_key_points:
            print(f"* {point}")

        # 4. Display document keywords
        if 'document_keywords' in data and data['document_keywords']:
            print("\n" + "---" + "\n")
            print("##  Document Keywords")
            print(", ".join(data['document_keywords']))

        print("\n" + "=" * 70)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    #  STEP 1: Replace with your actual Groq API key (gsk_...)
    API_KEY = "YOUR_GROQ_API_KEY_HERE"

    #  STEP 2: Define your input and output files
    TRANSCRIPT_FILE = "transcript.txt"
    OUTPUT_FILE = "structured_notes.json"

    # --- CRITICAL CHECK ---
    if "YOUR_GROQ_API_KEY_HERE" in API_KEY:
        print("\n" + "!" * 70)
        print("!!! CRITICAL ERROR: Please set a valid Groq API key in the API_KEY variable. !!!")
        print("!!! The script will not be able to connect to the LLM without it.          !!!")
        print("!" * 70 + "\n")
    else:
        try:
            # 1. Initialize the processor WITH Pegasus enabled
            processor = TextNotesProcessor(groq_api_key=API_KEY, use_pegasus=True)

            # 2. Process the text file and save the structured JSON output
            print(f"\nStarting processing pipeline for file: {TRANSCRIPT_FILE}")

            processor.process_text_file(
                text_file_path=TRANSCRIPT_FILE,
                output_json_path=OUTPUT_FILE,
                generate_mindmap=True  #  Auto-generate mindmap!
            )

            # 3. Generate the final console report from the saved JSON file
            processor.generate_final_report(OUTPUT_FILE)

            # 4. OPTIONAL: Generate custom mindmap from any concept
            print("\n" + "=" * 70)
            print(" BONUS: Custom Mindmap Generation")
            print("=" * 70)

            custom_concept = "Machine learning model training pipeline"
            processor.generate_mindmap(custom_concept, "custom_mindmap.mmd")

        except Exception as e:
            print(f"\nProcessing failed: {e}")
            print("Please check your Groq API key and ensure 'transcript.txt' exists.")
