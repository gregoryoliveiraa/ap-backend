from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.base_class import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    document_type = Column(String, nullable=False)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="documents")


class Template(Base):
    __tablename__ = "templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    type = Column(String, nullable=False)
    variables = Column(Text, nullable=True)  # Armazena variáveis no formato JSON
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    steps = Column(JSON, nullable=False)
    base_template = Column(Text)
    status = Column(String, default="active")
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    generated_documents = relationship("GeneratedDocument", back_populates="template")


class LegalThesis(Base):
    __tablename__ = "legal_theses"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    law_area = Column(String, nullable=False)
    topics = Column(JSON)
    legal_grounds = Column(JSON)
    source = Column(String)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    generated_documents = relationship("GeneratedDocument", 
                                    secondary="document_thesis_association", 
                                    back_populates="used_theses")


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    template_id = Column(String, ForeignKey("document_templates.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    form_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="generated_documents")
    template = relationship("DocumentTemplate", back_populates="generated_documents")
    used_theses = relationship("LegalThesis", 
                           secondary="document_thesis_association", 
                           back_populates="generated_documents")


# Association table for many-to-many relationship between GeneratedDocument and LegalThesis
class DocumentThesisAssociation(Base):
    __tablename__ = "document_thesis_association"

    document_id = Column(String, ForeignKey("generated_documents.id"), primary_key=True)
    thesis_id = Column(String, ForeignKey("legal_theses.id"), primary_key=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
