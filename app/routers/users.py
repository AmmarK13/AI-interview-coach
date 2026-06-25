from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import get_user_progress

router = APIRouter(tags=["User Progress"])

@router.get("/users/{user_id}/progress")
def read_user_progress(user_id: str, db: Session = Depends(get_db)):
    return get_user_progress(db, user_id)
