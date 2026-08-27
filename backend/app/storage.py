"""
Simple in-memory session store. No DB required per assignment constraints.
Keyed by session_id (uuid4 hex). Not thread-safe beyond what FastAPI's
single-worker dev/small deploy needs -- fine for this assignment's scope.
"""
import uuid
from typing import Any, Dict

_SESSIONS: Dict[str, Dict[str, Any]] = {}


def create_session() -> str:
    session_id = uuid.uuid4().hex
    _SESSIONS[session_id] = {
        "status": "created",
        "question_images": [],      
        "answer_images": [],        
        "questions": [],          
        "answer_blocks": [],        
        "word_boxes": {},           
        "image_sizes": {},          
        "mappings": [],            
        "grading": [],              
        "error": None,
    }
    return session_id


def get_session(session_id: str) -> Dict[str, Any]:
    if session_id not in _SESSIONS:
        raise KeyError(f"Unknown session_id: {session_id}")
    return _SESSIONS[session_id]


def update_session(session_id: str, **fields) -> None:
    session = get_session(session_id)
    session.update(fields)


def delete_session(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)