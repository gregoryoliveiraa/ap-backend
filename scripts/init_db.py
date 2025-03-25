# scripts/init_db.py
import sys
import os
import time
from pathlib import Path

# Adiciona o diretório pai ao path para importar a aplicação
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)
print(f"Adicionando ao path: {parent_dir}")

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.core.database import Base
    from app.core.security import get_password_hash
    from app.models.user import User
    import uuid
except ImportError as e:
    print(f"Erro ao importar: {e}")
    sys.exit(1)

def init_db():
    """
    Inicializa o banco de dados e cria um usuário administrador.
    """
    try:
        print("Criando conexão com o banco de dados...")
        # Converte para string para evitar problemas com MultiHostUrl
        db_url = str(settings.DATABASE_URL)
        print(f"URL do banco de dados: {db_url}")
        
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Importa todos os modelos para garantir que sejam registrados na Base
        print("Importando modelos...")
        from app.models.user import User
        from app.models.document import Document
        from app.models.chat import ChatHistory
        
        # Cria todas as tabelas
        print("Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        
        # Cria uma sessão
        db = SessionLocal()
        
        # Verifica se já existe algum usuário
        print("Verificando usuários existentes...")
        user_count = db.query(User).count()
        
        # Se não existir nenhum usuário, cria o administrador
        if user_count == 0:
            print("Criando usuário administrador...")
            admin = User(
                id=uuid.uuid4(),
                name="Admin",
                email="admin@advogadaparceira.com.br",
                password=get_password_hash("admin123"),  # Senha temporária
                oab_number="123456",
                oab_verified=True,
                credits=1000,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Usuário administrador criado com sucesso!")
        
        db.close()
        print("Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Inicializando o banco de dados...")
    init_db()
    print("Processo concluído!")