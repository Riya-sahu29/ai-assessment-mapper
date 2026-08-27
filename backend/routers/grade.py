from fastapi import APIRouter, HTTPException

from app import storage
from app.models.schemas import GradeResponse
from app.services import grading_service

router = APIRouter()


@router.post("/grade/{session_id}", response_model=GradeResponse)
async def grade_session(session_id: str):
    try:
        session = storage.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session["status"] != "done":
        raise HTTPException(status_code=400, detail="Run /process before grading.")

    questions_by_id = {q["id"]: q for q in session["questions"]}
    blocks_by_id = {b["id"]: b for b in session["answer_blocks"]}

    results = []
    for m in session["mappings"]:
        question = questions_by_id.get(m["question_id"])
        if not question:
            continue
        answer_text = " ".join(
            blocks_by_id[bid]["raw_text"]
            for bid in m.get("answer_block_ids", [])
            if bid in blocks_by_id
        )
        graded = grading_service.grade_answer(question["text"], answer_text)
        results.append({
            "question_id": question["id"],
            "marks_awarded": graded.get("marks_awarded"),
            "marks_total": graded.get("marks_total"),
            "correct": graded.get("correct"),
            "feedback": graded.get("feedback", ""),
        })

    summary = grading_service.summarize_grading(results)
    storage.update_session(session_id, grading=results)

    return GradeResponse(session_id=session_id, results=results, summary=summary)