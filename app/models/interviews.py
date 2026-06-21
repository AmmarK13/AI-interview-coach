from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from app.core.database import Base




class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(Text, default="Mock Interview")
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="sessions")
    responses = relationship("AudioResponse", back_populates="session")
