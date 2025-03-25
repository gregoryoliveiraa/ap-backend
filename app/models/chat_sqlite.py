# app/models/chat_sqlite.py
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship

from app.core.database_sqlite import Base

class ChatHistory(Base):
    __tablename__ = "chat_histories"

    # Para SQLite, usamos String para UUID
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String, nullable=True)
    
    # Armazena mensagens como JSON: [{"role": "user", "content": "msg"}, {"role": "assistant", "content": "resposta"}]
    messages = Column(JSON, nullable=False, default=list)
    
    # Relacionamento com o usuário que criou a conversa
    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", foreign_keys=[user_id])
    
    created_at = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, onupdate=func.now())