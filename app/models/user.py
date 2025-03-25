# app/models/user.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    oab_number = Column(String, unique=True, index=True, nullable=True)
    oab_verified = Column(Boolean, default=False)
    credits = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos serão definidos posteriormente para evitar importações circulares
    # documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    # chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")