from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nome_completo = Column(String, nullable=False)
    numero_oab = Column(String(50), nullable=True)
    estado_oab = Column(String(2), nullable=True)
    verificado = Column(Boolean, default=False)
    data_criacao = Column(DateTime, default=func.now())
    ultima_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    creditos_disponiveis = Column(Integer, default=0)
    plano = Column(String(50), default="gratuito")
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    usage = relationship("Usage", back_populates="user", uselist=False, cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="user", cascade="all, delete-orphan")
    # jurisprudencia_buscas = relationship("JurisprudenceSearch", back_populates="usuario")
    # documentos_gerados = relationship("GeneratedDocument", back_populates="usuario")
