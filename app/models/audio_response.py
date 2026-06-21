from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from app.core.database import Base


class AudioResponse(Base):
    __tablename__ = "audio_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"))
    audio_path = Column(Text, nullable=False)
    transcript = Column(Text)
    duration_seconds = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    session = relationship("InterviewSession", back_populates="responses")