from fastapi import APIRouter, Depends, File, UploadFile, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.answer_service import save_and_transcribe_answer, fetch_answer_details, fetch_or_create_evaluation, retry_evaluation

router = APIRouter(tags=["Answers & Evaluations"])

@router.post("/sessions/{session_id}/questions/{question_id}/answer")
def upload_answer(
    session_id: str,
    question_id: str,
    request: Request,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    transcribe_fn = getattr(request.app.state, "transcribe_fn", None)
    return save_and_transcribe_answer(db, session_id, question_id, audio_file, transcribe_fn=transcribe_fn)

@router.get("/sessions/{session_id}/questions/{question_id}/answer")
def get_answer(session_id: str, question_id: str, db: Session = Depends(get_db)):
    return fetch_answer_details(db, session_id, question_id)

@router.get("/sessions/{session_id}/questions/{question_id}/answer/evaluation")
def get_answer_evaluation(session_id: str, question_id: str, db: Session = Depends(get_db)):
    return fetch_or_create_evaluation(db, session_id, question_id)

@router.post("/sessions/{session_id}/questions/{question_id}/answer/evaluation/retry")
def retry_answer_evaluation(session_id: str, question_id: str, db: Session = Depends(get_db)):
    return retry_evaluation(db, session_id, question_id)
