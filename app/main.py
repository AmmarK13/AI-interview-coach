import os

from fastapi import FastAPI, File, HTTPException,Depends, UploadFile
from fastapi.responses import JSONResponse
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.answers import Answers
from app.models.questions import Question
from app.models.interviews import InterviewSession
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.util import save_upload
import uvicorn
from app.models.answer_evaluation import AnswerEvaluation
from app.utils.genrateQuestions import ExperienceLevel, QuestionType, Difficulty, genrate_questions as generate_questions_llm
from app.utils.transcribe import transcribe_audio
import uvicorn



pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class CreateSession(BaseModel):
    userid : str
    title:str
    role:str
    level: ExperienceLevel

class GenerateQuestionRequest(BaseModel):
    question_type: QuestionType
    difficulty: Difficulty





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
    
# @app.post("/sessions/{session_id}/upload-audio")
# def upload_audio(session_id: str, user_id: str, audio_file: UploadFile = File(...),db: Session = Depends(get_db)):
#     session = (
#         db.query(InterviewSession)
#         .filter(
#             InterviewSession.id == session_id,
#             InterviewSession.user_id == user_id
#         )
#         .first()
#     )
#     if not session:
#         raise HTTPException(status_code=404, detail="Session not found")

#     allowed_extensions = {".wav", ".mp3", ".qta"}
#     allowed_content_types = {
#         "audio/wav",
#         "audio/x-wav",
#         "audio/mpeg",
#         "audio/mp3",
#         "application/octet-stream",
#     }

#     file_extension = os.path.splitext(audio_file.filename or "")[1].lower()
#     if file_extension not in allowed_extensions:
#         raise HTTPException(status_code=400, detail="Only .wav, .mp3, and .qta files are allowed")

#     saved_path = save_upload(audio_file, "uploads/audio")

#     transcription_result = transcribe_audio_ammar(saved_path)
#     audio_response = AudioResponse(
#         session_id=session.id,
#         audio_path=saved_path,
#         transcript=transcription_result["transcript"],
#         duration_seconds=transcription_result["duration_seconds"],
#     )
#     db.add(audio_response)
#     db.commit()
#     db.refresh(audio_response)

#     return {
#         "message": "Audio uploaded and transcribed successfully",
#         "audio_response_id": str(audio_response.id),
#         "audio_path": audio_response.audio_path,
#         "transcript": audio_response.transcript,
#         "duration_seconds": audio_response.duration_seconds,
#     }


@app.get("/sessions/{session_id}/responses")
def get_audio_responses(session_id: str, db: Session = Depends(get_db)):
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_responses = (
        db.query(Answers)
        .filter(Answers.session_id == session.id)
        .order_by(Answers.created_at.asc())
        .all()
    )

    responses = [
        {
            "id": str(response.id),
            "audio_path": response.audio_path,
            "transcript": response.transcript,
            "duration_seconds": response.duration_seconds,
            "created_at": response.created_at.isoformat() if response.created_at else None
        }
        for response in db_responses
    ]

    return {
        "session_id": str(session.id),
        "responses": responses
    }

@app.get("/sessions/{session_id}/responses/{response_id}")
def get_audio_response_detail(session_id: str, response_id: str, db: Session = Depends(get_db)):
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    response = (
        db.query(Answers)
        .filter(
            Answers.id == response_id,
            Answers.session_id == session.id
        )
        .first()
    )
    if not response:
        raise HTTPException(status_code=404, detail="Audio response not found")

    return {
        "id": str(response.id),
        "audio_path": response.audio_path,
        "transcript": response.transcript,
        "duration_seconds": response.duration_seconds,
        "created_at": response.created_at.isoformat() if response.created_at else None
    }


@app.post("/sessions/{session_id}/questions/generate")
def generate_questions_endpoint(
    session_id: str,
    request:GenerateQuestionRequest,
    db: Session = Depends(get_db)
):
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    role = session.role
    level = session.level
    question_type = request.question_type
    difficulty = request.difficulty

    previous_questions = [
        question.question
        for question in (
            db.query(Question)
            .filter(Question.session_id == session.id)
            .order_by(Question.created_at.asc())
            .all()
        )
    ]

    try:
        question_data = generate_questions_llm(
            role,
            level,
            question_type,
            difficulty,
            previous_questions=previous_questions,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    question_index = (
        db.query(Question)
        .filter(Question.session_id == session.id)
        .count()
    )

    question = Question(
        session_id=session.id,
        question=question_data["question"]["question"],
        question_index=question_index,
        difficulty=question_data["question"]["difficulty"],
        question_type=question_data["question"]["question_type"],
    )
    db.add(question)

    db.commit()

    return {
        "session_id": str(session.id),
        "question_id": str(question.id),
        "generated_question": question_data["question"],
        "source": question_data.get("source", "gemini"),
    }
 


@app.get("/sessions/{session_id}/questions")
def get_questions(session_id: str, db: Session = Depends(get_db)):
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = (
        db.query(Question)
        .filter(Question.session_id == session.id)
        .order_by(Question.created_at.asc())
        .all()
    )

    return {
        "session_id": str(session.id),
        "questions": [
            {
                "id": str(question.id),
                "question": question.question,
                "question_index": question.question_index,
                "difficulty": question.difficulty,
                "question_type": question.question_type,
                "created_at": question.created_at.isoformat() if question.created_at else None
            }
            for question in questions
        ]
    }

@app.get("/sessions/{session_id}/questions/{question_id}")
def get_question_detail(session_id: str, question_id: str, db: Session = Depends(get_db)):
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    question = (
        db.query(Question)
        .filter(
            Question.id == question_id,
            Question.session_id == session.id
        )
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return {
        "id": str(question.id),
        "question": question.question,
        "question_index": question.question_index,
        "difficulty": question.difficulty,
        "question_type": question.question_type,
        "created_at": question.created_at.isoformat() if question.created_at else None
    }


@app.post("/sessions/{session_id}/questions/{question_id}/answer")
def upload_answer(session_id: str, question_id: str, audio_file: UploadFile = File(...),db: Session = Depends(get_db)):
        session= db.query(InterviewSession).filter(InterviewSession.id==session_id).first()
        if not session:
            raise HTTPException(status_code=404,detail="Session not found")
        question= db.query(Question).filter(Question.id==question_id).first()
        if not question:
            raise HTTPException(status_code=404,detail="Question not found")
        if str(question.session_id) != str(session.id):
            raise HTTPException(
                status_code=400,
                detail="Question does not belong to this session"
                )
        
        
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
        if audio_file.content_type not in allowed_content_types:
            raise HTTPException(
            status_code=400,
            detail="Invalid audio content type"
            )
        try:

            saved_path = save_upload(audio_file, "uploads/audio")

            transcript= transcribe_audio(saved_path)

            answer = Answers(
                session_id= session.id,
                questions_id=question.id,
                audio_path= saved_path,
                transcript= transcript["transcript"],
                duration_seconds= transcript["duration_seconds"]
            )
            db.add(answer)
            db.commit()
            db.refresh(answer)

            return{
                "message": "Answer transcribed successfully",
                "answer_id":str(answer.id),
                "session_id":str(session_id),
                "question_id":str(question_id),
                "path":saved_path,
                "transcript":transcript["transcript"],
                "duration_seconds":transcript["duration_seconds"]
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
            status_code=500,
            detail=str(e)
            )


    
    



if __name__ == "__main__":
    print("🚀 Starting AI Interview Coach API...")
    print("📊 Database tables initialized")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
