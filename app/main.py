from fastapi import FastAPI, HTTPException,Depends
from fastapi.responses import JSONResponse
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.interviews import InterviewSession
from app.models.audio_response import AudioResponse
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.database import get_db
import uvicorn

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

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
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    password_hash = pwd_context.hash(payload.password)
    
    # Create new user with hashed password
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


if __name__ == "__main__":
    print("🚀 Starting AI Interview Coach API...")
    print("📊 Database tables initialized")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
