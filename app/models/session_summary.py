from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, func,Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from app.core.database import Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum



class SessionSummary(Base):
    __tablename__="session_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id",ondelete="CASCADE"),unique=True,index=True)
    overall_score = Column(Numeric(3,1), nullable=False)
    total_questions = Column(Integer,nullable=False)
    answered_questions =  Column(Integer,nullable=False)
    avg_score_behavioral= Column(Numeric(3,1),nullable=False)
    avg_score_technical= Column(Numeric(3,1),nullable=False)
    avg_score_situational= Column(Numeric(3,1),nullable=False)
    highest_score = Column(Numeric(3,1),nullable=False)
    lowest_score=Column(Numeric(3,1),nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    session = relationship(
        "InterviewSession",
        back_populates="summary"
    )