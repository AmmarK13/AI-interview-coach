from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from app.core.database import Base


class Answers(Base):
    __tablename__="answers"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    questions_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"),nullable=False,index=True)
    audio_path = Column(Text,nullable=False)
    transcript= Column(Text,nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    duration_seconds=Column(Integer)
    created_at=Column(TIMESTAMP, server_default=func.now())
    
    question = relationship("Question", back_populates="answer")
    evaluation = relationship("AnswerEvaluation", back_populates="answer", uselist=False)
