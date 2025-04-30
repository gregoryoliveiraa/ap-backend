#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicionar o diretório pai ao path para importar módulos do app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar modelos e configurações
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.core.security import get_password_hash

def init_local_db():
    """
    Inicializa o banco de dados local com a estrutura correta
    """
    logger.info("Iniciando inicialização do banco de dados local...")
    
    try:
        # Criar todas as tabelas
        logger.info("Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
        
        # Criar sessão
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Verificar se já existe um usuário admin
        admin_user = db.query(User).filter(User.email == "admin@advogadaparceira.com.br").first()
        
        if not admin_user:
            logger.info("Criando usuário administrador...")
            # Criar usuário admin
            admin_user = User(
                email="admin@advogadaparceira.com.br",
                hashed_password=get_password_hash("admin123"),
                first_name="Administrador",
                last_name="do Sistema",
                is_active=True,
                is_admin=True,
                plan="admin",
                token_credits=1000,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            logger.info("Usuário administrador criado com sucesso!")
        else:
            logger.info("Usuário administrador já existe.")
        
        # Verificar se já existe um usuário de teste
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not test_user:
            logger.info("Criando usuário de teste...")
            # Criar usuário de teste
            test_user = User(
                email="test@example.com",
                hashed_password=get_password_hash("test123"),
                first_name="Usuário",
                last_name="de Teste",
                is_active=True,
                is_admin=False,
                plan="basic",
                token_credits=100,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(test_user)
            db.commit()
            logger.info("Usuário de teste criado com sucesso!")
        else:
            logger.info("Usuário de teste já existe.")
        
        logger.info("Inicialização do banco de dados local concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a inicialização do banco de dados: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_local_db() 