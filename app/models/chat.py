# app/models/chat.py
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

from app.core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=True)
    # Armazena mensagens como JSON: [{"role": "user", "content": "msg"}, {"role": "assistant", "content": "resposta"}]
    messages = Column(JSON, nullable=False, default=list)
    
    # Relacionamento com o usuário que criou a conversa
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="chat_histories")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

# Adiciona a relação no modelo User
from app.models.user import User
User.chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")