import re
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app import storage
from app.models.schemas import ProcessResponse
from app.services import ai_extraction, highlight_service, ocr_service, mapping_service
from app.services.pdf_utils import b64_png_to_image

router = APIRouter()


def _slugify_number(number: str, seen: set) -> str:
    base = "q" + re.sub(r"[^a-z0-9]+", "", number.lower())
    slug = base
    n = 2
    while slug in seen:
        slug = f"{base}_{n}"
        n += 1
    seen.add(slug)
    return slug


@router.post("/process/{session_id}", response_model=ProcessResponse)
async def process_session(session_id: str):
    try:
        session = storage.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        # 1. Extract questions from the question paper (vision)
        storage.update_session(session_id, status="extracting_questions")
        raw_questions = ai_extraction.extract_questions(session["question_images"])
        seen_ids: set = set()
        questions = [
            {"id": _slugify_number(q["number"] or f"q{i}", seen_ids),
             "number": q["number"] or f"Q{i+1}",
             "text": q["text"]}
            for i, q in enumerate(raw_questions)
        ]

        # 2. OCR the answer sheet for word-level bounding boxes (for later highlighting)
        storage.update_session(session_id, status="running_ocr")
        word_boxes_by_page: Dict[int, List[Dict[str, Any]]] = {}
        for i, b64 in enumerate(session["answer_images"]):
            img = b64_png_to_image(b64)
            word_boxes_by_page[i] = ocr_service.get_word_boxes(img)

        # 3. Transcribe handwritten answers (vision)
        storage.update_session(session_id, status="extracting_answers")
        raw_blocks = ai_extraction.extract_answer_blocks(session["answer_images"])
        answer_blocks = [
            {"id": f"block_{i}", "page": b["page"], "raw_text": b["text"],
             "visible_number": b["visible_number"]}
            for i, b in enumerate(raw_blocks)
        ]

        # 4. Map answer blocks to questions (text reasoning)
        storage.update_session(session_id, status="mapping")
        mapping_result = mapping_service.map_answers_to_questions(questions, answer_blocks)
        mappings = mapping_result.get("mappings", [])
        unmatched_ids = mapping_result.get("unmatched_block_ids", [])

        # 5. Locate highlight regions for each mapped answer block
        storage.update_session(session_id, status="locating_highlights")
        blocks_by_id = {b["id"]: b for b in answer_blocks}
        for m in mappings:
            boxes = []
            for block_id in m.get("answer_block_ids", []):
                block = blocks_by_id.get(block_id)
                if not block:
                    continue
                page = block["page"]
                w, h = session["image_sizes"].get(page, (0, 0))
                if not w or not h:
                    continue
                box = highlight_service.locate_answer_block(
                    block["raw_text"], word_boxes_by_page.get(page, []), w, h
                )
                if box:
                    boxes.append({"page": page, **box})
            m["highlight_boxes"] = boxes
            m["located"] = len(boxes) > 0
            m.setdefault("confidence", 0.5)

        storage.update_session(
            session_id,
            status="done",
            questions=questions,
            answer_blocks=answer_blocks,
            word_boxes=word_boxes_by_page,
            mappings=mappings,
        )

        return ProcessResponse(
            session_id=session_id,
            status="done",
            questions=questions,
            answer_blocks=answer_blocks,
            mappings=mappings,
            unmatched_blocks=unmatched_ids,
        )

    except Exception as e:
        storage.update_session(session_id, status="error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")


@router.get("/status/{session_id}")
async def get_status(session_id: str):
    try:
        session = storage.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": session_id, "status": session["status"], "error": session.get("error")}


@router.get("/session/{session_id}/page/answer/{page_index}")
async def get_answer_page_image(session_id: str, page_index: int):
    """Returns the base64 PNG for a given answer-sheet page, for the frontend viewer."""
    try:
        session = storage.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.")
    images = session["answer_images"]
    if page_index < 0 or page_index >= len(images):
        raise HTTPException(status_code=404, detail="Page not found.")
    w, h = session["image_sizes"].get(page_index, (0, 0))
    return {"page": page_index, "image_b64": images[page_index], "width": w, "height": h}