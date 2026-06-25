from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.interviews import InterviewSession
from app.models.questions import Question
from app.schemas.sessions import GenerateQuestionRequest
from app.utils.genrateQuestions import genrate_questions as generate_questions_llm

def generate_and_save_question(
    db: Session,
    session_id: str,
    request: GenerateQuestionRequest
) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    role = session.role
    level = session.level
    question_type = request.question_type
    difficulty = request.difficulty

    previous_questions = [
        q.question
        for q in (
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
    db.refresh(question)

    return {
        "session_id": str(session.id),
        "question_id": str(question.id),
        "generated_question": question_data["question"],
        "source": question_data.get("source", "gemini"),
    }

def fetch_questions_for_session(db: Session, session_id: str) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
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

def fetch_question_detail(db: Session, session_id: str, question_id: str) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
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
