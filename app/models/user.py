from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from app.core.database import Base


class User(Base):
    __tablename__="users"

    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    email = Column(Text,unique=True)
    password_hash = Column(Text, nullable=False) 
    created_at = Column(TIMESTAMP, server_default=func.now())

    sessions = relationship("InterviewSession", back_populates="user")