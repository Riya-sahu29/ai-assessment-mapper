import json
import re
import time
from typing import Any, Dict, List

from groq import Groq, BadRequestError, APIStatusError

from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

MAPPING_PROMPT_TEMPLATE = """You are mapping a student's answer blocks to the correct questions
from a question paper. The answer blocks may be in the WRONG ORDER, some questions may be
UNANSWERED, and some answer blocks may not clearly match ANY question.

These blocks/questions could NOT be confidently matched by exact number label, so use the
content itself to decide.

QUESTIONS (id, number, text):
{questions_json}

ANSWER BLOCKS (id, page, visible_number if the student wrote one, transcribed text):
{blocks_json}

Instructions:
- For each question, decide which answer_block id(s) answer it (usually one, but an answer
  can legitimately span multiple blocks/pages -- include all that apply).
- A question with no matching block gets status "unanswered" and an empty answer_block_ids list.
- Every answer block must be accounted for. Any block that best fits no question should be
  listed in "unmatched_block_ids" instead of forced onto a question.
- Set confidence 0.0-1.0 for each mapping based on how sure you are.

Return ONLY valid JSON, no markdown, no commentary, in this exact shape:
{{
  "mappings": [
    {{"question_id": "q11a", "answer_block_ids": ["block_2"], "status": "answered", "confidence": 0.92}},
    {{"question_id": "q12", "answer_block_ids": [], "status": "unanswered", "confidence": 1.0}}
  ],
  "unmatched_block_ids": ["block_5"]
}}
"""


def _normalize_number(n: str) -> str:
    """'11 (a)' -> '11a', 'Ans 10.' -> '10', 'Q3' -> '3' -- for exact comparison."""
    n = re.sub(r"(?i)^ans\.?\s*", "", (n or "").strip())
    n = re.sub(r"(?i)^q\.?\s*", "", n)
    return re.sub(r"[^a-z0-9]", "", n.lower())


def _safe_json(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}


def _deterministic_pass(
    questions: List[Dict[str, Any]],
    answer_blocks: List[Dict[str, Any]],
) -> tuple:
    """Directly pair questions and blocks whose numbers match exactly.
    This is far more reliable than LLM reasoning for labeled answers,
    and shrinks what's left for the LLM to reason about."""
    q_by_norm: Dict[str, List[Dict[str, Any]]] = {}
    for q in questions:
        q_by_norm.setdefault(_normalize_number(q["number"]), []).append(q)

    matched_mappings = []
    matched_question_ids = set()
    matched_block_ids = set()

    for b in answer_blocks:
        vn = _normalize_number(b.get("visible_number") or "")
        if not vn:
            continue
        candidates = q_by_norm.get(vn)
        if not candidates:
            continue
        # exact, unambiguous label match
        q = candidates[0]
        matched_mappings.append({
            "question_id": q["id"],
            "answer_block_ids": [b["id"]],
            "status": "answered",
            "confidence": 1.0,
        })
        matched_question_ids.add(q["id"])
        matched_block_ids.add(b["id"])

    remaining_questions = [q for q in questions if q["id"] not in matched_question_ids]
    remaining_blocks = [b for b in answer_blocks if b["id"] not in matched_block_ids]
    return matched_mappings, remaining_questions, remaining_blocks


def _llm_pass(
    questions: List[Dict[str, Any]],
    answer_blocks: List[Dict[str, Any]],
    retries: int = 1,
) -> Dict[str, Any]:
    if not questions and not answer_blocks:
        return {"mappings": [], "unmatched_block_ids": []}

    prompt = MAPPING_PROMPT_TEMPLATE.format(
        questions_json=json.dumps(questions, indent=2),
        blocks_json=json.dumps(answer_blocks, indent=2),
    )

    result: Dict[str, Any] = {}
    last_err = None

    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=settings.TEXT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=4000,
                reasoning_effort="low",
            )
            result = _safe_json(resp.choices[0].message.content)
            if result.get("mappings") is not None:
                break
            last_err = "empty/invalid JSON from mapping model"
        except (BadRequestError, APIStatusError) as e:
            last_err = str(e)
            time.sleep(0.5)
        except Exception as e:
            last_err = str(e)
            time.sleep(0.5)

    if result.get("mappings") is None:
        raise RuntimeError(f"Answer-to-question mapping failed: {last_err}")

    return result


def map_answers_to_questions(
    questions: List[Dict[str, Any]],
    answer_blocks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    # 1. Deterministic exact-number matches first -- trustworthy, no LLM needed
    det_mappings, remaining_questions, remaining_blocks = _deterministic_pass(
        questions, answer_blocks
    )

    # 2. LLM reasoning only for what's left (unlabeled or ambiguous blocks/questions)
    llm_result = _llm_pass(remaining_questions, remaining_blocks)

    all_mappings = det_mappings + llm_result.get("mappings", [])
    unmatched_block_ids = llm_result.get("unmatched_block_ids", [])

    mapped_question_ids = {m["question_id"] for m in all_mappings}
    for q in questions:
        if q["id"] not in mapped_question_ids:
            all_mappings.append({
                "question_id": q["id"],
                "answer_block_ids": [],
                "status": "unanswered",
                "confidence": 1.0,
            })

    return {"mappings": all_mappings, "unmatched_block_ids": unmatched_block_ids}