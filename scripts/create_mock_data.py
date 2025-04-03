#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.security import get_password_hash
from app.db.session import Base
from app.models.user import User
from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Function to create test users
def create_test_users():
    print("Creating test users...")
    
    # Admin user
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin_user:
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            nome_completo="Admin User",
            verificado=True,
            plano="premium",
            creditos_disponiveis=1000,
            data_criacao=datetime.utcnow(),
            ultima_atualizacao=datetime.utcnow()
        )
        db.add(admin)
    
    # Test user
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        test = User(
            email="test@example.com",
            hashed_password=get_password_hash("test123"),
            nome_completo="Test User",
            numero_oab="123456",
            estado_oab="SP",
            verificado=True,
            plano="basico",
            creditos_disponiveis=100,
            data_criacao=datetime.utcnow(),
            ultima_atualizacao=datetime.utcnow()
        )
        db.add(test)
    
    # Free user
    free_user = db.query(User).filter(User.email == "free@example.com").first()
    if not free_user:
        free = User(
            email="free@example.com",
            hashed_password=get_password_hash("free123"),
            nome_completo="Free User",
            verificado=False,
            plano="gratuito",
            creditos_disponiveis=10,
            data_criacao=datetime.utcnow(),
            ultima_atualizacao=datetime.utcnow()
        )
        db.add(free)
    
    db.commit()
    
    # Return users for creating related data
    return {
        "admin": db.query(User).filter(User.email == "admin@example.com").first(),
        "test": db.query(User).filter(User.email == "test@example.com").first(),
        "free": db.query(User).filter(User.email == "free@example.com").first()
    }

# Function to create test documents
def create_test_documents(users):
    print("Creating test documents...")
    
    # Define document types and templates
    document_types = [
        "Contrato", "Petição", "Parecer", "Notificação", "Procuração"
    ]
    
    # Create documents for each user
    for user_key, user in users.items():
        # Skip if user already has documents
        existing_docs = db.query(Document).filter(Document.usuario_id == user.id).count()
        if existing_docs > 0:
            continue
            
        # Create multiple documents for each user
        num_docs = 10 if user_key == "admin" else 5 if user_key == "test" else 2
        
        for i in range(num_docs):
            doc_type = random.choice(document_types)
            doc_title = f"{doc_type} - {i+1}"
            
            # Create document with random date in the last 30 days
            days_ago = random.randint(0, 30)
            doc_date = datetime.utcnow() - timedelta(days=days_ago)
            
            doc = Document(
                titulo=doc_title,
                conteudo=f"Conteúdo exemplo para {doc_title}",
                tipo=doc_type.lower(),
                categoria="juridico" if i % 2 == 0 else "administrativo",
                status="finalizado" if i % 3 == 0 else "rascunho",
                usuario_id=user.id,
                data_criacao=doc_date,
                ultima_atualizacao=doc_date
            )
            db.add(doc)
    
    db.commit()

# Function to create test chat sessions and messages
def create_test_chat_sessions(users):
    print("Creating test chat sessions...")
    
    # Create chat sessions for each user
    for user_key, user in users.items():
        # Skip if user already has chat sessions
        existing_sessions = db.query(ChatSession).filter(ChatSession.usuario_id == user.id).count()
        if existing_sessions > 0:
            continue
            
        # Create multiple chat sessions for each user
        num_sessions = 5 if user_key == "admin" else 3 if user_key == "test" else 1
        
        for i in range(num_sessions):
            # Create session with random date in the last 30 days
            days_ago = random.randint(0, 30)
            session_date = datetime.utcnow() - timedelta(days=days_ago)
            
            session_title = f"Consulta {i+1}"
            
            session = ChatSession(
                titulo=session_title,
                usuario_id=user.id,
                data_criacao=session_date,
                ultima_atualizacao=session_date
            )
            db.add(session)
            db.flush()  # Flush to get the session ID
            
            # Create messages for the session
            num_messages = random.randint(3, 10)
            
            # First message from user
            first_message = ChatMessage(
                conteudo="Olá, gostaria de fazer uma consulta sobre direito do consumidor.",
                role="user",
                sessao_id=session.id,
                data_criacao=session_date,
                usuario_id=user.id
            )
            db.add(first_message)
            
            # Response from assistant
            response_time = session_date + timedelta(minutes=1)
            response = ChatMessage(
                conteudo="Olá! Como posso ajudá-lo com questões de direito do consumidor?",
                role="assistant",
                sessao_id=session.id,
                data_criacao=response_time,
                usuario_id=None
            )
            db.add(response)
            
            # Additional messages
            current_time = response_time
            for j in range(num_messages - 2):
                current_time += timedelta(minutes=random.randint(1, 5))
                
                if j % 2 == 0:
                    # User message
                    message = ChatMessage(
                        conteudo=f"Pergunta de teste número {j+1} sobre consumidor.",
                        role="user",
                        sessao_id=session.id,
                        data_criacao=current_time,
                        usuario_id=user.id
                    )
                else:
                    # Assistant message
                    message = ChatMessage(
                        conteudo=f"Resposta para a pergunta {j} sobre direito do consumidor.",
                        role="assistant",
                        sessao_id=session.id,
                        data_criacao=current_time,
                        usuario_id=None
                    )
                
                db.add(message)
    
    db.commit()

# Main function to create all test data
def create_all_test_data():
    # Create test users
    users = create_test_users()
    
    # Create test documents
    create_test_documents(users)
    
    # Create test chat sessions
    create_test_chat_sessions(users)
    
    print("Mock data creation completed successfully!")

if __name__ == "__main__":
    create_all_test_data() 