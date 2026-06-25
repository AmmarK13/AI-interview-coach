from sqlalchemy.orm import Session
from app.models.user_progress import UserProgress
from sqlalchemy import func
from app.models.user_progress import UserProgress
from app.models.session_summary import SessionSummary
from app.models.interviews import InterviewSession, Status


def build_user_progress(
    db: Session,
    user_id: str
) -> UserProgress:

    completed_sessions = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == Status.complete
        )
        .all()
    )

    if not completed_sessions:
        return None

    session_ids = [session.id for session in completed_sessions]

    summaries = (
        db.query(SessionSummary)
        .filter(SessionSummary.session_id.in_(session_ids))
        .all()
    )

    if not summaries:
        return None

    scores = [float(summary.overall_score) for summary in summaries]

    progress = UserProgress(
        user_id=user_id,
        interviews_completed=len(summaries),
        avg_score=round(sum(scores) / len(scores), 1),
        best_score=max(scores),
    )

    db.add(progress)
    db.commit()
    db.refresh(progress)

    return progress


def update_user_progress(
    db: Session,
    user_id: str
):
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id)
        .first()
    )

    if not progress:
        return build_user_progress(
            db,
            user_id
        )

    completed_sessions = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == Status.complete
        )
        .all()
    )

    session_ids = [s.id for s in completed_sessions]

    summaries = (
        db.query(SessionSummary)
        .filter(SessionSummary.session_id.in_(session_ids))
        .all()
    )

    scores = [float(s.overall_score) for s in summaries]

    progress.interviews_completed = len(scores)
    progress.avg_score = round(
        sum(scores) / len(scores),
        1
    )
    progress.best_score = max(scores)

    db.commit()
    db.refresh(progress)

    return progress