from __future__ import annotations

import os
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.models.interviews import InterviewSession
from app.models.questions import Question
from app.models.answers import Answers
from app.models.answer_evaluation import AnswerEvaluation
from app.utils.util import save_upload
from app.utils.transcribe import transcribe_audio
from app.utils.evaluateAnswers import evaluate_answer

def save_and_transcribe_answer(
    db: Session,
    session_id: str,
    question_id: str,
    audio_file: UploadFile,
    transcribe_fn = None
) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
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
        saved_path = save_upload(audio_file, "audio/answers")
        if transcribe_fn is None:
            transcribe_fn = transcribe_audio
        transcript_data = transcribe_fn(saved_path)

        answer = Answers(
            session_id=session.id,
            questions_id=question.id,
            audio_path=saved_path,
            transcript=transcript_data["transcript"],
            duration_seconds=transcript_data["duration_seconds"]
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)

        return {
            "message": "Answer transcribed successfully",
            "answer_id": str(answer.id),
            "session_id": str(session_id),
            "question_id": str(question_id),
            "path": saved_path,
            "transcript": transcript_data["transcript"],
            "answer": answer.transcript,
            "duration_seconds": transcript_data["duration_seconds"]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

def fetch_answer_details(db: Session, session_id: str, question_id: str) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if str(question.session_id) != str(session.id):
        raise HTTPException(
            status_code=400,
            detail="Question does not belong to this session"
        )

    answer = db.query(Answers).filter(Answers.session_id == session.id, Answers.questions_id == question.id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    return {
        "answer_id": str(answer.id),
        "session_id": str(session.id),
        "question_id": str(question.id),
        "audio_path": answer.audio_path,
        "transcript": answer.transcript,
        "duration_seconds": answer.duration_seconds,
        "created_at": answer.created_at.isoformat() if answer.created_at else None
    }

def fetch_or_create_evaluation(db: Session, session_id: str, question_id: str) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if str(question.session_id) != str(session.id):
        raise HTTPException(
            status_code=400,
            detail="Question does not belong to this session"
        )

    answer = db.query(Answers).filter(Answers.session_id == session.id, Answers.questions_id == question.id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    if not answer.audio_path:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    evaluation = (
        db.query(AnswerEvaluation)
        .filter(AnswerEvaluation.answer_id == answer.id)
        .order_by(AnswerEvaluation.created_at.desc())
        .first()
    )
    if not evaluation:
        eval_data = evaluate_answer(question.question, answer.transcript)
        evaluation = AnswerEvaluation(
            answer_id=answer.id,
            score=eval_data["score"],
            strengths=eval_data["strengths"],
            weaknesses=eval_data["weaknesses"],
            feedback=eval_data["feedback"],
            improved_answer=eval_data["improved_answer"],
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
    
    return {
        "answer_id": str(answer.id),
        "answer": answer.transcript,
        "score": float(evaluation.score),
        "strengths": evaluation.strengths,
        "weaknesses": evaluation.weaknesses,
        "feedback": evaluation.feedback,
        "improved_answer": evaluation.improved_answer,
    }

def retry_evaluation(db: Session, session_id: str, question_id: str) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if str(question.session_id) != str(session.id):
        raise HTTPException(
            status_code=400,
            detail="Question does not belong to this session"
        )

    answer = db.query(Answers).filter(Answers.session_id == session.id, Answers.questions_id == question.id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    if not answer.audio_path:
        raise HTTPException(status_code=404, detail="Answer not found")

    eval_data = evaluate_answer(question.question, answer.transcript)
    evaluation = AnswerEvaluation(
        answer_id=answer.id,
        score=eval_data["score"],
        strengths=eval_data["strengths"],
        weaknesses=eval_data["weaknesses"],
        feedback=eval_data["feedback"],
        improved_answer=eval_data["improved_answer"],
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return {
        "evaluation_id": str(evaluation.id),
        "answer_id": str(answer.id),
        "answer": answer.transcript,
        "score": float(evaluation.score),
        "strengths": evaluation.strengths,
        "weaknesses": evaluation.weaknesses,
        "feedback": evaluation.feedback,
        "improved_answer": evaluation.improved_answer,
        "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None
    }

def fetch_audio_responses(db: Session, session_id: str) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
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

def fetch_audio_response_detail(db: Session, session_id: str, response_id: str) -> dict:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
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
