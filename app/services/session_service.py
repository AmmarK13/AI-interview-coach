from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.answers import Answers
from app.models.questions import Question,QuestionType
from app.models.interviews import InterviewSession
from app.models.answer_evaluation import AnswerEvaluation
from app.models.session_summary import SessionSummary
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

def fetch_session_by_id(
    db: Session,
    session_id: str,
    user_id: str
) -> InterviewSession:

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session

def validate_session_complete(
    db: Session,
    session_id: str
) -> None:

    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    questions = (
        db.query(Question)
        .filter(Question.session_id == session_id)
        .all()
    )

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="Session contains no questions"
        )

    answers = (
        db.query(Answers)
        .filter(Answers.session_id == session_id)
        .all()
    )

    answered_question_ids = {
        str(answer.questions_id)
        for answer in answers
    }

    missing_answers = [
        question.question_index
        for question in questions
        if str(question.id) not in answered_question_ids
    ]

    if missing_answers:
        raise HTTPException(
            status_code=400,
            detail=f"Questions not answered: {missing_answers}"
        )

    evaluations = (
        db.query(AnswerEvaluation)
        .filter(
            AnswerEvaluation.answer_id.in_(
                [answer.id for answer in answers]
            )
        )
        .all()
    )

    evaluated_answer_ids = {
        str(evaluation.answer_id)
        for evaluation in evaluations
    }

    missing_evaluations = [
        str(answer.id)
        for answer in answers
        if str(answer.id) not in evaluated_answer_ids
    ]

    if missing_evaluations:
        raise HTTPException(
            status_code=400,
            detail="Some answers have not been evaluated yet"
        )
    
def build_session_summary(
    db: Session,
    session_id: str
) -> SessionSummary:

    questions = (
        db.query(Question)
        .filter(Question.session_id == session_id)
        .all()
    )

    answers = (
        db.query(Answers)
        .filter(Answers.session_id == session_id)
        .all()
    )

    evaluations = (
        db.query(AnswerEvaluation)
        .join(
            Answers,
            AnswerEvaluation.answer_id == Answers.id
        )
        .filter(Answers.session_id == session_id)
        .all()
    )

    total_questions = len(questions)
    answered_questions = len(answers)

    scores = [float(e.score) for e in evaluations]

    overall_score = round(sum(scores) / len(scores), 1)
    highest_score = max(scores)
    lowest_score = min(scores)

    answer_map = {
        str(answer.questions_id): answer.id
        for answer in answers
    }

    evaluation_map = {
        str(e.answer_id): float(e.score)
        for e in evaluations
    }

    technical_scores = []
    behavioral_scores = []
    situational_scores = []

    for question in questions:

        answer_id = answer_map.get(str(question.id))

        if not answer_id:
            continue

        score = evaluation_map.get(str(answer_id))

        if score is None:
            continue

        if question.question_type == QuestionType.technical:
            technical_scores.append(score)

        elif question.question_type == QuestionType.behavioral:
            behavioral_scores.append(score)

        elif question.question_type == QuestionType.situational:
            situational_scores.append(score)

    avg_score_technical = (
        round(sum(technical_scores) / len(technical_scores), 1)
        if technical_scores
        else 0.0
    )

    avg_score_behavioral = (
        round(sum(behavioral_scores) / len(behavioral_scores), 1)
        if behavioral_scores
        else 0.0
    )

    avg_score_situational = (
        round(sum(situational_scores) / len(situational_scores), 1)
        if situational_scores
        else 0.0
    )

    summary = SessionSummary(
        session_id=session_id,
        overall_score=overall_score,
        total_questions=total_questions,
        answered_questions=answered_questions,
        avg_score_behavioral=avg_score_behavioral,
        avg_score_technical=avg_score_technical,
        avg_score_situational=avg_score_situational,
        highest_score=highest_score,
        lowest_score=lowest_score,
    )

    db.add(summary)
    db.commit()
    db.refresh(summary)

    return summary


def fetch_session_summary(
    db: Session,
    session_id: str
) -> SessionSummary:

    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    summary = (
        db.query(SessionSummary)
        .filter(SessionSummary.session_id == session_id)
        .first()
    )

    if not summary:
        raise HTTPException(
            status_code=404,
            detail="Session summary not found"
        )

    return summary