import json
import re
import time
from typing import Any, Dict, List

from groq import Groq, BadRequestError, APIStatusError

from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


QUESTION_PROMPT = """You are reading a printed question paper page.
Extract EVERY question on this page, in the exact order they are printed.

Rules:
- Treat labelled sub-parts as SEPARATE entries. Example: "11 (a)" and "11 (b)" must
  be two separate entries, not one.
- Preserve the original printed numbering exactly as shown (e.g. "11 (a)", "Q3", "2.4").
- Include the full question text for each entry.
- If this page has no questions (cover page, instructions page), return an empty list.

Return ONLY valid JSON, no markdown, no commentary, in this exact shape:
{"questions": [{"number": "11 (a)", "text": "full question text here"}]}
"""

ANSWER_PROMPT = """You are reading a page of a student's HANDWRITTEN answer sheet.
Transcribe the handwriting into text, split into logical blocks (a new block whenever
the student appears to move to a new question/answer).

Rules:
- If the student wrote a visible question number/label next to a block (e.g. "Q11(a)",
  "11 a)", "Ans 3"), capture it in "visible_number" exactly as written. If no number is
  visible, set "visible_number" to null.
- Do your best on messy handwriting; if a word is illegible, use "[illegible]" inline
  rather than skipping it.
- Preserve blocks even if they seem to answer nothing recognizable (unmatched attempts
  should still be transcribed, not dropped).
- If the page is blank or has no handwriting, return an empty list.

Return ONLY valid JSON, no markdown, no commentary, in this exact shape:
{"blocks": [{"visible_number": "11 (a)", "text": "transcribed answer text"}]}
"""


def _call_vision(prompt: str, image_b64: str, retries: int = 1) -> Dict[str, Any]:
    """Call the vision model. Returns {} on failure instead of raising,
    so one bad page never crashes the whole /process request."""
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=settings.VISION_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            },
                        },
                    ],
                }],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=3500,
            )
            raw = resp.choices[0].message.content
            parsed = _safe_json(raw)
            if parsed:
                return parsed
            last_err = "empty/invalid JSON from model"
        except (BadRequestError, APIStatusError) as e:
            last_err = str(e)
            time.sleep(0.5)
        except Exception as e:
            last_err = str(e)
            time.sleep(0.5)

    print(f"[_call_vision] giving up after {retries + 1} attempt(s): {last_err}")
    return {}


def _safe_json(raw: str) -> Dict[str, Any]:
    """Vision models occasionally wrap JSON in markdown fences despite instructions."""
    if not raw:
        return {}
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}


def extract_questions(page_images_b64: List[str]) -> List[Dict[str, str]]:
    all_questions = []
    for img_b64 in page_images_b64:
        result = _call_vision(QUESTION_PROMPT, img_b64)
        for q in result.get("questions", []):
            all_questions.append({"number": q.get("number", "").strip(),
                                   "text": q.get("text", "").strip()})
    return all_questions


def extract_answer_blocks(page_images_b64: List[str]) -> List[Dict[str, Any]]:
    all_blocks = []
    for page_idx, img_b64 in enumerate(page_images_b64):
        result = _call_vision(ANSWER_PROMPT, img_b64)
        for b in result.get("blocks", []):
            all_blocks.append({
                "page": page_idx,
                "visible_number": (b.get("visible_number") or "").strip() or None,
                "text": b.get("text", "").strip(),
            })
    return all_blocks