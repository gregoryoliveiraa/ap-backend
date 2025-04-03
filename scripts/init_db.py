#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.security import get_password_hash

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Create a temporary Base class to avoid circular dependencies
Base = declarative_base()

class TempUser(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nome_completo = Column(String(255), nullable=False)
    hashed_password = Column("senha_hash", String(255), nullable=False)
    numero_oab = Column(String(50), nullable=True)
    estado_oab = Column(String(2), nullable=True)
    verificado = Column(Boolean, default=False)
    data_criacao = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    ultima_atualizacao = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    creditos_disponiveis = Column(Integer, default=0)
    plano = Column(String(50), default="gratuito")

def init_db():
    # Create admin user if it doesn't exist
    admin_email = "admin@example.com"
    admin_password = "admin123"  # In production, use a secure password
    
    # Check if the admin user already exists
    query = text("SELECT id FROM usuarios WHERE email = :email")
    result = db.execute(query, {"email": admin_email}).fetchone()
    
    if not result:
        print(f"Creating admin user: {admin_email}")
        # Insert admin user directly using SQL to avoid circular dependencies
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        insert_query = text("""
            INSERT INTO usuarios (
                email, nome_completo, senha_hash, verificado, 
                plano, creditos_disponiveis, data_criacao, ultima_atualizacao
            ) VALUES (
                :email, :nome, :senha, :verificado, 
                :plano, :creditos, :data_criacao, :ultima_atualizacao
            )
        """)
        
        db.execute(insert_query, {
            "email": admin_email,
            "nome": "Administrator",
            "senha": get_password_hash(admin_password),
            "verificado": True,
            "plano": "premium",
            "creditos": 1000,
            "data_criacao": now,
            "ultima_atualizacao": now
        })
        db.commit()
        print("Admin user created successfully!")
    else:
        print(f"Admin user {admin_email} already exists.")
    
    # Print credentials for login
    print("\nAdmin credentials for login:")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")

if __name__ == "__main__":
    # Create only the usuarios table if it doesn't exist
    # This avoids circular dependencies with other models
    inspector = inspect(engine)
    if not inspector.has_table("usuarios"):
        TempUser.__table__.create(engine)
        print("Created usuarios table")
    
    init_db() 