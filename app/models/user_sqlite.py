# app/models/user_sqlite.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship

from app.core.database_sqlite import Base

class User(Base):
    __tablename__ = "users"

    # Para SQLite, usamos String para UUID
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    oab_number = Column(String, unique=True, index=True, nullable=True)
    oab_verified = Column(Boolean, default=False)
    credits = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos serão definidos posteriormente para evitar importações circulares
    # documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    # chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")