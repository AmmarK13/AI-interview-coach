from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class VoiceOutput(Base):
    __tablename__ = "voice_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("answer_evaluations.id", ondelete="CASCADE"), nullable=True, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=True, index=True)
    text_content = Column(Text, nullable=False)
    audio_path = Column(Text, nullable=False)
    voice_model = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    evaluation = relationship("AnswerEvaluation", back_populates="voice_outputs")
    question = relationship("Question", back_populates="voice_outputs")
