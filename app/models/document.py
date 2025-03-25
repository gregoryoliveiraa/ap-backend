# app/models/document_sqlite.py
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship

from app.core.database_sqlite import Base

class Document(Base):
    __tablename__ = "documents"

    # Para SQLite, usamos String para UUID
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String, nullable=False)  # petição, contrato, parecer, etc.
    
    # Para SQLite, usamos JSON em vez de ARRAY
    tags = Column(JSON, nullable=True)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    
    # Relacionamento com o usuário que criou o documento
    created_by = Column(String, ForeignKey("users.id"))
    user = relationship("User", foreign_keys=[created_by])
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())