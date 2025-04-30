from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.base_class import Base
from app.core.security import get_password_hash
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    oab_number = Column(String, unique=True, nullable=True)
    estado_oab = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    plan = Column(String, default='basic')
    token_credits = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    bio = Column(Text)
    available_credits = Column(Float, default=0)
    
    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    document_folders = relationship("DocumentFolder", back_populates="user", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="user", cascade="all, delete-orphan")
    usages = relationship("Usage", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.hashed_password = get_password_hash(password)

    def calculate_consumed_credits(self) -> float:
        total = 0
        for usage in self.usages:
            total += usage.credits_used
        return total

    @property
    def nome_completo(self) -> str:
        """Combine first_name and last_name for backwards compatibility"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""
