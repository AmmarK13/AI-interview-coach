from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.answer_service import fetch_audio_responses, fetch_audio_response_detail

router = APIRouter(tags=["Responses"])

@router.get("/sessions/{session_id}/responses")
def get_audio_responses(session_id: str, db: Session = Depends(get_db)):
    return fetch_audio_responses(db, session_id)

@router.get("/sessions/{session_id}/responses/{response_id}")
def get_audio_response_detail(session_id: str, response_id: str, db: Session = Depends(get_db)):
    return fetch_audio_response_detail(db, session_id, response_id)
