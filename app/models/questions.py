from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from app.core.database import Base
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class QuestionType(str, Enum):
    behavioral = "behavioral"
    technical = "technical"
    situational = "situational"

class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class Question(Base):
    __tablename__="questions"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"),index=True)
    question= Column(Text, nullable=False)
    question_index = Column(Integer, nullable=False)
    difficulty= Column(SQLEnum(Difficulty),nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    session = relationship("InterviewSession", back_populates="question")
    answer = relationship("Answer", back_populates="question")
