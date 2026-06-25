from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, func,Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from app.core.database import Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum


class UserProgress(Base):
    __tablename__="user_progress"

    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id",ondelete="CASCADE"), unique=True,index=True)
    interviews_completed= Column(Integer, nullable=False)
    avg_score = Column(Numeric(3,1),nullable=False)
    best_score =Column(Numeric(3,1),nullable=False)
    last_updated = Column (TIMESTAMP, server_default=func.now(),nullable=False)

    user = relationship(
    "User",
    back_populates="progress"
)
