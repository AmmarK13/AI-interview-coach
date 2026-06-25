from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user_progress import UserProgress
from app.services.user_service import build_user_progress

router = APIRouter(tags=["User Progress"])

@router.get("/users/{user_id}/progress")
def get_user_progress(
    user_id: str,
    db: Session = Depends(get_db)
) -> dict:

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id)
        .first()
    )

    if not progress:
        progress = build_user_progress(
            db,
            user_id
        )

    if not progress:
        return {
            "interviews_completed": 0,
            "avg_score": None,
            "best_score": None,
            "last_updated": None,
            "message": "No completed sessions yet."
        }

    return {
        "interviews_completed": progress.interviews_completed,
        "avg_score": float(progress.avg_score),
        "best_score": float(progress.best_score),
        "last_updated": (
            progress.last_updated.isoformat()
            if progress.last_updated
            else None
        )
    }