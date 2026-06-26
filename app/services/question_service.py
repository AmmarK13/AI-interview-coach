from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.interviews import InterviewSession
from app.models.questions import Question
from app.models.voice_output import VoiceOutput
from app.models.answer_evaluation import AnswerEvaluation
from app.models.answers import Answers
from app.schemas.sessions import GenerateQuestionRequest
from app.utils.genrateQuestions import genrate_questions as generate_questions_llm
import os
import uuid

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

def speak_question(db: Session, session_id: str, question_id: str) -> str:
    question = (
        db.query(Question)
        .filter(
            Question.id == question_id,
            Question.session_id == session_id
        )
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    voice_output = (
        db.query(VoiceOutput)
        .filter(VoiceOutput.question_id == question_id)
        .first()
    )

    if voice_output and os.path.exists(voice_output.audio_path):
        return voice_output.audio_path

    # Otherwise generate TTS
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    target_dir = os.path.join(project_root, "app", "audio", "question")
    os.makedirs(target_dir, exist_ok=True)

    audio_filename = f"question_{uuid.uuid4().hex}.wav"
    audio_path = os.path.join(target_dir, audio_filename)

    from app.utils.tts import text_to_speech
    try:
        text_to_speech(question.question, audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

    new_output = VoiceOutput(
        question_id=question.id,
        text_content=question.question,
        audio_path=audio_path,
        voice_model="piper/en_US-lessac-medium"
    )
    db.add(new_output)
    db.commit()
    db.refresh(new_output)

    return audio_path

def speak_evaluation(db: Session, session_id: str, question_id: str) -> str:
    # Get the question
    question = (
        db.query(Question)
        .filter(
            Question.id == question_id,
            Question.session_id == session_id
        )
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Get the answer
    answer = (
        db.query(Answers)
        .filter(
            Answers.questions_id == question_id,
            Answers.session_id == session_id
        )
        .first()
    )
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found for this question")

    evaluation = (
        db.query(AnswerEvaluation)
        .filter(AnswerEvaluation.answer_id == answer.id)
        .order_by(AnswerEvaluation.created_at.desc())
        .first()
    )

    if not evaluation:
        # If the evaluation doesn't exist, create it!
        from app.utils.evaluateAnswers import evaluate_answer
        try:
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
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to generate evaluation: {e}")

    # Check if a voice output already exists for this evaluation
    voice_output = (
        db.query(VoiceOutput)
        .filter(VoiceOutput.evaluation_id == evaluation.id)
        .first()
    )

    if voice_output and os.path.exists(voice_output.audio_path):
        return voice_output.audio_path

    # Otherwise generate TTS
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    target_dir = os.path.join(project_root, "app", "audio", "question")
    os.makedirs(target_dir, exist_ok=True)

    audio_filename = f"evaluation_{uuid.uuid4().hex}.wav"
    audio_path = os.path.join(target_dir, audio_filename)

    from app.utils.tts import text_to_speech
    try:
        text_to_speech(evaluation.feedback, audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

    new_output = VoiceOutput(
        evaluation_id=evaluation.id,
        text_content=evaluation.feedback,
        audio_path=audio_path,
        voice_model="piper/en_US-lessac-medium"
    )
    db.add(new_output)
    db.commit()
    db.refresh(new_output)

    return audio_path
