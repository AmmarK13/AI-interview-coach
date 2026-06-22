import os

from fastapi import FastAPI, File, HTTPException,Depends, UploadFile
from fastapi.responses import JSONResponse
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.questions import Question
from app.models.interviews import InterviewSession
from app.models.audio_response import AudioResponse
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.util import save_upload
from app.utils.transcribe_ammar import transcribe_audio_ammar
import uvicorn
from enum import Enum

class ExperienceLevel(str, Enum):
    intern = "intern"
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class CreateSession(BaseModel):
    userid : str
    title:str
    role:str
    level: ExperienceLevel



class RegisterUser(BaseModel):
    email : EmailStr
    password: str= Field(min_length=8,max_length=128)

class LoginUser(BaseModel):
    email: EmailStr
    password: str

app = FastAPI(
    title="AI Interview Coach",
    description="AI-powered mock interview platform",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Welcome to the AI Interview Coach API!"}

@app.get("/health")
def health_check():
    """Health check endpoint to verify API is running."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "API is running successfully",
            "service": "AI Interview Coach"
        }
    )

@app.post("/auth/register")
def register(payload: RegisterUser , db : Session = Depends(get_db)):
    """Register a new user with email and password."""
    
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = pwd_context.hash(payload.password)
    
    user = User(email=payload.email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User registered successfully",
        "user_id": str(user.id),
        "email": user.email
    }

@app.post("/auth/login")
def login(payload: LoginUser, db: Session =Depends(get_db )):
    """Login user with email and password."""
    
    
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not pwd_context.verify(payload.password, user.password_hash):

        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    
    return {
        "message": "Login successful",
        "user_id": str(user.id),
        "email": user.email
    }



@app.post("/sessions")
def create_session(payload:CreateSession , db: Session=Depends(get_db)):
    #check if user exist
    user = db.query(User).filter(User.id==payload.userid).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    #create a session
    ss= InterviewSession(
        user_id= payload.userid,
        title=payload.title,
        role = payload.role,
        level = payload.level
    )
    #commit the session
    db.add(ss)
    db.commit()
    db.refresh(ss)
    
    return {
        "message": "Session created successfully",
        "session_id": str(ss.id),
        "user_id": str(ss.user_id),
        "title": ss.title,
        "role": ss.role,
        "level":ss.level,
        "created_at": ss.created_at.isoformat() if ss.created_at else None
    }

@app.get("/sessions")
def get_sessions(userid:str, db: Session=Depends(get_db)):
    #check if user exist
    user = db.query(User).filter(User.id==userid).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    
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

@app.get("/sessions/{session_id}")
def get_session(session_id : str, user_id:str,db : Session=Depends(get_db)):
     session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id
        )
        .first()
    )
     if not session:
         raise HTTPException(status_code=404,detail="Session not found")
     return {
         "session-id":session.id,
         "title":session.title,
         "role": session.role,
         "level":session.level,
         "created-at":session.created_at
     }
    
@app.post("/sessions/{session_id}/upload-audio")
def upload_audio(session_id: str, user_id: str, audio_file: UploadFile = File(...),db: Session = Depends(get_db)):
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

    allowed_extensions = {".wav", ".mp3", ".qta"}
    allowed_content_types = {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "application/octet-stream",
    }

    file_extension = os.path.splitext(audio_file.filename or "")[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only .wav, .mp3, and .qta files are allowed")

    saved_path = save_upload(audio_file, "uploads/audio")

    transcription_result = transcribe_audio_ammar(saved_path)
    audio_response = AudioResponse(
        session_id=session.id,
        audio_path=saved_path,
        transcript=transcription_result["transcript"],
        duration_seconds=transcription_result["duration_seconds"],
    )
    db.add(audio_response)
    db.commit()
    db.refresh(audio_response)

    return {
        "message": "Audio uploaded and transcribed successfully",
        "audio_response_id": str(audio_response.id),
        "audio_path": audio_response.audio_path,
        "transcript": audio_response.transcript,
        "duration_seconds": audio_response.duration_seconds,
    }


if __name__ == "__main__":
    print("🚀 Starting AI Interview Coach API...")
    print("📊 Database tables initialized")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
