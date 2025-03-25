# scripts/init_db_sqlite.py
import sys
import os
import time
from pathlib import Path

# Adiciona o diretório pai ao path para importar a aplicação
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)
print(f"Adicionando ao path: {parent_dir}")

try:
    # Importa a configuração SQLite
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import sessionmaker
    
    # Usa o módulo database_sqlite
    from app.core.database_sqlite import Base, engine, SessionLocal
    from app.core.security import get_password_hash
    import uuid
    
    def init_db():
        """
        Inicializa o banco de dados SQLite e cria um usuário administrador.
        """
        try:
            print("Conectando ao banco de dados SQLite...")
            
            # Importa todos os modelos para garantir que sejam registrados na Base
            print("Importando modelos...")
            from app.models.user_sqlite import User
            from app.models.document_sqlite import Document
            from app.models.chat_sqlite import ChatHistory
            
            # Cria todas as tabelas com uma ordem explícita
            print("Criando tabelas...")
            # Primeiro criamos tabelas sem dependências
            Base.metadata.create_all(bind=engine, tables=[User.__table__])
            # Depois criamos tabelas com dependências
            Base.metadata.create_all(bind=engine, tables=[Document.__table__, ChatHistory.__table__])
            
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
            print("Banco de dados SQLite inicializado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados SQLite: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    if __name__ == "__main__":
        print("Inicializando o banco de dados SQLite...")
        init_db()
        print("Processo concluído!")
        
except ImportError as e:
    print(f"Erro ao importar: {e}")
    sys.exit(1)