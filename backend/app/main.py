from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import grade, process, upload

app = FastAPI(title="AI Assessment Extraction & Answer Mapping")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["upload"])
app.include_router(process.router, tags=["process"])
app.include_router(grade.router, tags=["grade"])


@app.get("/")
async def root():
    return {"status": "ok", "service": "ai-assessment-mapper-backend"}