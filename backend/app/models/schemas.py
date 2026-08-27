from typing import List, Literal, Optional
from pydantic import BaseModel


class Question(BaseModel):
    id: str            
    number: str       
    text: str


class AnswerBlock(BaseModel):
    id: str             
    page: int           
    raw_text: str
    visible_number: Optional[str] = None  


class BBox(BaseModel):
    page: int
    x_pct: float
    y_pct: float
    width_pct: float
    height_pct: float


class Mapping(BaseModel):
    question_id: str
    answer_block_ids: List[str]
    status: Literal["answered", "unanswered", "unmatched"]
    confidence: float
    highlight_boxes: List[BBox] = []
    located: bool = False


class GradingResult(BaseModel):
    question_id: str
    marks_awarded: Optional[float] = None
    marks_total: Optional[float] = None
    correct: Optional[bool] = None
    feedback: str


class UploadResponse(BaseModel):
    session_id: str
    question_pages: int
    answer_pages: int


class ProcessResponse(BaseModel):
    session_id: str
    status: str
    questions: List[Question]
    answer_blocks: List[AnswerBlock]
    mappings: List[Mapping]
    unmatched_blocks: List[str]  


class GradeResponse(BaseModel):
    session_id: str
    results: List[GradingResult]
    summary: str