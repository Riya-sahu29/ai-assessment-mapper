import json
import re
from typing import Any, Dict, List

from groq import Groq

from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

GRADE_PROMPT_TEMPLATE = """Grade this student's answer against the question. Be fair and concise.

Question: {question_text}

Student's answer: {answer_text}

Return ONLY valid JSON, no markdown, in this exact shape:
{{"correct": true, "marks_awarded": 4, "marks_total": 5, "feedback": "one or two sentence feedback"}}

If the answer is missing/blank, set correct false, marks_awarded 0, and feedback explaining
it was left unanswered.
"""


def _safe_json(raw: str) -> Dict[str, Any]:
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"correct": None, "marks_awarded": None, "marks_total": None,
                 "feedback": "Could not generate feedback."}


def grade_answer(question_text: str, answer_text: str) -> Dict[str, Any]:
    prompt = GRADE_PROMPT_TEMPLATE.format(
        question_text=question_text,
        answer_text=answer_text or "(no answer found)",
    )
    resp = client.chat.completions.create(
    model=settings.TEXT_MODEL,
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},
    temperature=0,
    max_tokens=1024,
    extra_body={"reasoning_effort": "low"},

    )
    return _safe_json(resp.choices[0].message.content)


def summarize_grading(results: List[Dict[str, Any]]) -> str:
    total_awarded = sum(r.get("marks_awarded") or 0 for r in results)
    total_possible = sum(r.get("marks_total") or 0 for r in results)
    answered = sum(1 for r in results if r.get("marks_awarded") is not None)
    return (
        f"{answered}/{len(results)} questions evaluated. "
        f"Score: {total_awarded}/{total_possible}."
    )