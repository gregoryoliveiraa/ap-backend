# app/core/database_sqlite.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define o caminho para o arquivo SQLite
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sql_app.db')}"

# Imprime o caminho do banco de dados para debug
print(f"SQLite database path: {SQLITE_DATABASE_URL}")

# Cria o engine do SQLAlchemy
# Note: `check_same_thread=False` só é necessário para SQLite
engine = create_engine(
    SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
)

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