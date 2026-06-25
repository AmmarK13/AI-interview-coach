from sqlalchemy.orm import Session
from app.models.user_progress import UserProgress

def get_user_progress(db: Session, user_id: str) -> dict:
    progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
    if progress is None:
        return {
            "interviews_completed": 0,
            "avg_score": None,
            "best_score": None,
            "last_updated": None,
            "message": "No completed sessions yet."
        }
    return {
        "interviews_completed": progress.interviews_completed,
        "avg_score": float(progress.avg_score) if progress.avg_score is not None else None,
        "best_score": float(progress.best_score) if progress.best_score is not None else None,
        "last_updated": progress.last_updated.isoformat() if progress.last_updated else None
    }
