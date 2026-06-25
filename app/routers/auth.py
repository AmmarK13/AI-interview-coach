from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import RegisterUser, LoginUser
from app.services.auth_service import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register(payload: RegisterUser, db: Session = Depends(get_db)):
    """Register a new user with email and password."""
    return register_user(db, payload)

@router.post("/login")
def login(payload: LoginUser, db: Session = Depends(get_db)):
    """Login user with email and password."""
    return authenticate_user(db, payload)
