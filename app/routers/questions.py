from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.question_service import speak_question, speak_evaluation

router = APIRouter(tags=["Questions"])

@router.post("/sessions/{session_id}/questions/{question_id}/speak")
def get_question_speech(session_id: str, question_id: str, db: Session = Depends(get_db)):
    audio_path = speak_question(db, session_id, question_id)
    return FileResponse(audio_path, media_type="audio/mpeg")

@router.post("/sessions/{session_id}/questions/{question_id}/answer/evaluation/speak")
def get_evaluation_speech(session_id: str, question_id: str, db: Session = Depends(get_db)):
    audio_path = speak_evaluation(db, session_id, question_id)
    return FileResponse(audio_path, media_type="audio/mpeg")
