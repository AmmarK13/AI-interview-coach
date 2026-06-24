from sqlalchemy import Column, Text, TIMESTAMP, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    answer_id = Column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Numeric(3, 1), nullable=False)
    strengths = Column(ARRAY(Text), nullable=False)
    weaknesses = Column(ARRAY(Text), nullable=False)
    feedback = Column(Text, nullable=False)
    improved_answer = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    answer = relationship("Answer", back_populates="evaluation")