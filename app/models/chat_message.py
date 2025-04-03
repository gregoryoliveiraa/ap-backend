from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.base_class import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    provider = Column(String, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages") 