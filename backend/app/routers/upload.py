from fastapi import APIRouter, File, HTTPException, UploadFile

from app import storage
from app.models.schemas import UploadResponse
from app.services.pdf_utils import file_to_page_images, image_to_b64_png

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_files(
    question_paper: UploadFile = File(...),
    answer_sheet: UploadFile = File(...),
):
    q_bytes = await question_paper.read()
    a_bytes = await answer_sheet.read()

    if not q_bytes or not a_bytes:
        raise HTTPException(status_code=400, detail="Both files are required and must not be empty.")

    try:
        q_pages = file_to_page_images(question_paper.filename, q_bytes)
        a_pages = file_to_page_images(answer_sheet.filename, a_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded files: {e}")

    session_id = storage.create_session()
    storage.update_session(
        session_id,
        status="uploaded",
        question_images=[image_to_b64_png(p) for p in q_pages],
        answer_images=[image_to_b64_png(p) for p in a_pages],
        image_sizes={i: p.size for i, p in enumerate(a_pages)},
    )

    return UploadResponse(
        session_id=session_id,
        question_pages=len(q_pages),
        answer_pages=len(a_pages),
    )