from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.sessions import CreateSession, GenerateQuestionRequest
from app.services.session_service import create_new_session, fetch_sessions_by_user, fetch_session_by_id
from app.services.question_service import generate_and_save_question, fetch_questions_for_session, fetch_question_detail

router = APIRouter(tags=["Sessions & Questions"])

@router.post("/sessions")
def create_session(payload: CreateSession, db: Session = Depends(get_db)):
    return create_new_session(db, payload)

@router.get("/sessions")
def get_sessions(userid: str, db: Session = Depends(get_db)):
    return fetch_sessions_by_user(db, userid)

@router.get("/sessions/{session_id}")
def get_session(session_id: str, user_id: str, db: Session = Depends(get_db)):
    return fetch_session_by_id(db, session_id, user_id)

@router.post("/sessions/{session_id}/questions/generate")
def generate_question(
    session_id: str,
    request: GenerateQuestionRequest,
    db: Session = Depends(get_db)
):
    return generate_and_save_question(db, session_id, request)

@router.get("/sessions/{session_id}/questions")
def get_questions(session_id: str, db: Session = Depends(get_db)):
    return fetch_questions_for_session(db, session_id)

@router.get("/sessions/{session_id}/questions/{question_id}")
def get_question(session_id: str, question_id: str, db: Session = Depends(get_db)):
    return fetch_question_detail(db, session_id, question_id)
