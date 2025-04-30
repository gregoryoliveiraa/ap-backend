from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Criar base
Base = declarative_base()

# Definir modelo User com a estrutura real da tabela
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String)
    hashed_password = Column(String)
    nome_completo = Column(String)
    numero_oab = Column(String(50))
    estado_oab = Column(String(2))
    verificado = Column(Boolean)
    data_criacao = Column(DateTime)
    ultima_atualizacao = Column(DateTime)
    creditos_disponiveis = Column(Integer)
    plano = Column(String(50))
    is_active = Column(Boolean)
    role = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Configuração do banco de dados SQLite
DATABASE_URL = "sqlite:///./app.db"

# Criar engine e sessão
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def list_users():
    try:
        users = db.query(User).all()
        print("\nLista de Usuários:")
        print("-" * 120)
        print(f"{'ID':<36} | {'Email':<30} | {'Nome':<30} | {'OAB':<10} | {'Plano':<10} | {'Créditos':<8} | {'Role':<10} | {'Ativo':<5}")
        print("-" * 120)
        
        for user in users:
            print(f"{str(user.id):<36} | {user.email:<30} | {user.nome_completo:<30} | {user.numero_oab or '':<10} | {user.plano or '':<10} | {user.creditos_disponiveis or 0:<8} | {user.role:<10} | {'Sim' if user.is_active else 'Não':<5}")
        
        print("-" * 120)
        print(f"Total de usuários: {len(users)}")
        
    except Exception as e:
        print(f"Erro ao listar usuários: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users() 