from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from uuid import uuid4

class Usage(Base):
    __tablename__ = "usage"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    total_tokens = Column(Integer, default=0)
    available_tokens = Column(Integer, default=0)
    total_documents = Column(Integer, default=0)
    chat_history = Column(JSON, default=list)
    document_history = Column(JSON, default=list)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="usages") 