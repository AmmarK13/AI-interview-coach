from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.sessions import CreateSession, GenerateQuestionRequest,SessionComplete,Status
from app.models.interviews import InterviewSession
from app.services.session_service import create_new_session, fetch_sessions_by_user, fetch_session_by_id,validate_session_complete,build_session_summary,fetch_session_summary
from app.services.question_service import generate_and_save_question, fetch_questions_for_session, fetch_question_detail
from app.services.user_service import update_user_progress

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


@router.post("/session/{session_id}/complete")
def complete_session(
    payload: SessionComplete,
    db: Session = Depends(get_db)
):
    session = fetch_session_by_id(
        db,
        payload.sessionid,
        payload.userid
    )

    if session.status == Status.complete:
        raise HTTPException(
            status_code=400,
            detail="Cannot complete session twice"
        )

    validate_session_complete(
        db,
        payload.sessionid
    )

    print("Validation complete")

    summary = build_session_summary(
        db,
        payload.sessionid
    )

    print("Session summary built")

    session_obj = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == payload.sessionid)
        .first()
    )

    session_obj.status = Status.complete

    db.commit()
    update_user_progress(db,payload.userid)

    return {
        "Message": "Successfuly created summary"
    }

@router.get("/session/{session_id}/summary")
def get_summary(
    session_id: str,
    db: Session = Depends(get_db)
):
    summary = fetch_session_summary(
        db,
        session_id
    )

    return {
        "summary_id": str(summary.id),
        "session_id": str(summary.session_id),
        "overall_score": float(summary.overall_score),
        "total_questions": summary.total_questions,
        "answered_questions": summary.answered_questions,
        "avg_score_technical": float(summary.avg_score_technical),
        "avg_score_behavioral": float(summary.avg_score_behavioral),
        "avg_score_situational": float(summary.avg_score_situational),
        "highest_score": float(summary.highest_score),
        "lowest_score": float(summary.lowest_score),
        "created_at": (
            summary.created_at.isoformat()
            if summary.created_at
            else None
        )
    }

@router.get("/user/{user_id}/sessions/history")
def get_history(user_id: str, db: Session = Depends(get_db)):
    # Retrieve user sessions data
    user_data = fetch_sessions_by_user(db, user_id)
    sessions = user_data.get("sessions", [])

    history: dict = {}
    for sess in sessions:
        # Attempt to fetch a summary; if none exists (e.g., session not completed), skip
        try:
            summary = fetch_session_summary(db, str(sess["id"]))
        except HTTPException as exc:
            if exc.status_code == 404:
                # No summary yet for this session – ignore it
                continue
            raise
        history[sess["id"]] = summary
    return history
        
   
