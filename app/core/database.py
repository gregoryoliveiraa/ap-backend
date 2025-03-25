# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Cria a URL do banco de dados a partir das configurações
# Convertemos para string para evitar problemas com MultiHostUrl
SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URL)

# Cria o engine do SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria uma sessão local para interagir com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos SQLAlchemy
Base = declarative_base()

# Função para obter uma sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()