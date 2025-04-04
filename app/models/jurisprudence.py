from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from app.db.base_class import Base


class JurisprudenceSearch(Base):
    __tablename__ = "jurisprudencia_buscas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    termos_busca = Column(Text, nullable=False)
    filtros = Column(JSONB)
    timestamp = Column(DateTime, default=func.now())
    resultados_encontrados = Column(Integer, default=0)
    
    # Relationships
    usuario = relationship("User", back_populates="jurisprudencia_buscas")
    resultados = relationship("JurisprudenceResult", back_populates="busca", cascade="all, delete-orphan")


class JurisprudenceResult(Base):
    """
    Model to store jurisprudence search results (not in original schema but useful)
    """
    __tablename__ = "jurisprudencia_resultados"

    id = Column(Integer, primary_key=True, index=True)
    busca_id = Column(Integer, ForeignKey("jurisprudencia_buscas.id"))
    titulo = Column(String(255), nullable=False)
    tribunal = Column(String(50), nullable=False)
    numero_processo = Column(String(100))
    data_julgamento = Column(DateTime)
    relator = Column(String(100))
    ementa = Column(Text, nullable=False)
    inteiro_teor = Column(Text)
    url_original = Column(String(255))
    relevancia = Column(Integer, default=0)  # Relevance score
    
    # Relationships
    busca = relationship("JurisprudenceSearch", back_populates="resultados")
