from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.interviews import InterviewSession
from app.schemas.sessions import CreateSession

def create_new_session(db: Session, payload: CreateSession) -> dict:
    user = db.query(User).filter(User.id == payload.userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ss = InterviewSession(
        user_id=payload.userid,
        title=payload.title,
        role=payload.role,
        level=payload.level
    )
    db.add(ss)
    db.commit()
    db.refresh(ss)
    
    return {
        "message": "Session created successfully",
        "session_id": str(ss.id),
        "user_id": str(ss.user_id),
        "title": ss.title,
        "role": ss.role,
        "level": ss.level,
        "created_at": ss.created_at.isoformat() if ss.created_at else None
    }

def fetch_sessions_by_user(db: Session, userid: str) -> dict:
    user = db.query(User).filter(User.id == userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": str(user.id),
        "email": user.email,
        "sessions": [
            {
                "id": str(session.id),
                "title": session.title,
                "role": session.role,
                "level": session.level,
                "created_at": session.created_at.isoformat() if session.created_at else None
            }
            for session in user.sessions
        ]
    }

def fetch_session_by_id(db: Session, session_id: str, user_id: str) -> dict:
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session-id": session.id,
        "title": session.title,
        "role": session.role,
        "level": session.level,
        "created-at": session.created_at
    }
