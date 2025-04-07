#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string
import random
from passlib.context import CryptContext
from datetime import datetime
from app.models.user import User
from app.db.session import engine
from sqlalchemy.orm import Session
import sys

# Lista de emails para criar usuários
USERS_TO_CREATE = [
    {
        "email": "sidarta.martins@gmail.com",
        "nome_completo": "Sidarta Martins",
    },
    {
        "email": "gregory.oliveiraa@hotmail.com",
        "nome_completo": "Gregory Oliveira",
    },
    {
        "email": "djalmaborgesmartins@gmail.com",
        "nome_completo": "Djalma Borges Martins",
    },
    {
        "email": "pagotto@freitasleite.com.br",
        "nome_completo": "Pagotto Freitas Leite",
    },
    {
        "email": "leayassuda@gmail.com",
        "nome_completo": "Lea Yassuda",
    },
    {
        "email": "righettimirela@gmail.com",
        "nome_completo": "Mirela Righetti",
    },
]

# Configuração para senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_strong_password(length=12):
    """Gera uma senha forte aleatória"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    # Garante pelo menos um de cada tipo
    password = (
        random.choice(string.ascii_lowercase) +
        random.choice(string.ascii_uppercase) +
        random.choice(string.digits) +
        random.choice('!@#$%^&*()_+-=')
    )
    # Completa o resto da senha
    password += ''.join(random.choice(characters) for _ in range(length - 4))
    
    # Mistura os caracteres
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)

def create_user(email, nome_completo, password=None, creditos=1000, plano="premium", verificado=True):
    """Cria um usuário no banco de dados"""
    
    # Gera uma senha forte se não for fornecida
    if not password:
        password = generate_strong_password()
    
    # Gera o hash da senha
    hashed_password = pwd_context.hash(password)
    
    with Session(engine) as session:
        # Verifica se o usuário já existe
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Usuário com email {email} já existe!")
            if existing_user.creditos_disponiveis != creditos:
                # Atualiza o saldo de créditos se diferente
                existing_user.creditos_disponiveis = creditos
                session.commit()
                print(f"Saldo atualizado para {creditos} créditos.")
            return False, None
        
        # Cria o novo usuário
        new_user = User(
            email=email,
            nome_completo=nome_completo,
            hashed_password=hashed_password,
            verificado=verificado,
            creditos_disponiveis=creditos,
            plano=plano,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(new_user)
        session.commit()
        print(f"Usuário criado com sucesso!")
        print(f"Email: {email}")
        print(f"Senha: {password}")
        print(f"Créditos: {creditos}")
        
        return True, password

def main():
    """Função principal para criar todos os usuários"""
    print("Iniciando criação de usuários...")
    
    created_users = []
    
    for user_data in USERS_TO_CREATE:
        email = user_data["email"]
        nome_completo = user_data["nome_completo"]
        
        print(f"\nProcessando usuário: {email}")
        success, password = create_user(
            email=email,
            nome_completo=nome_completo,
            creditos=1000,
            plano="premium",
            verificado=True
        )
        
        if success and password:
            created_users.append({
                "email": email,
                "nome_completo": nome_completo,
                "senha": password
            })
    
    # Exibe resumo dos usuários criados
    if created_users:
        print("\n=== RESUMO DOS USUÁRIOS CRIADOS ===")
        for user in created_users:
            print(f"Email: {user['email']}")
            print(f"Nome: {user['nome_completo']}")
            print(f"Senha: {user['senha']}")
            print("-" * 40)
    
    print("\nProcesso concluído!")

if __name__ == "__main__":
    main() 