from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from app.core.database import Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum


class ExperienceLevel(str, Enum):
    intern = "intern"
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"



class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),index=True)
    title = Column(Text, default="Mock Interview")
    created_at = Column(TIMESTAMP, server_default=func.now())
    role = Column(Text, nullable=False)
    level = Column(SQLEnum(ExperienceLevel),nullable=False)




    user = relationship("User", back_populates="sessions")
    questions=relationship("Question",back_populates="session")
