#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import string
import random
import sqlite3
from datetime import datetime
from passlib.context import CryptContext
from uuid import uuid4

# Configuração para senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

def create_user_direct(conn, email, nome_completo, password=None, creditos=1000, plano="premium", verificado=True):
    """Cria um usuário diretamente no banco de dados SQLite"""
    
    cursor = conn.cursor()
    
    # Gera uma senha forte se não for fornecida
    if not password:
        password = generate_strong_password()
    
    # Gera o hash da senha
    hashed_password = pwd_context.hash(password)
    
    # Gera um ID único
    user_id = str(uuid4())
    
    # Verifica se o usuário já existe
    cursor.execute("SELECT id, creditos_disponiveis FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        print(f"Usuário com email {email} já existe!")
        user_id, existing_credits = existing_user
        
        if existing_credits != creditos:
            # Atualiza o saldo de créditos se diferente
            cursor.execute(
                "UPDATE users SET creditos_disponiveis = ? WHERE id = ?",
                (creditos, user_id)
            )
            conn.commit()
            print(f"Saldo atualizado para {creditos} créditos.")
        return False, None
    
    # Data atual
    now = datetime.utcnow().isoformat()
    
    # Insere o novo usuário
    cursor.execute("""
        INSERT INTO users (
            id, email, nome_completo, hashed_password, 
            verificado, creditos_disponiveis, plano,
            is_active, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, email, nome_completo, hashed_password,
        verificado, creditos, plano,
        True, now, now
    ))
    
    conn.commit()
    print(f"Usuário criado com sucesso!")
    print(f"Email: {email}")
    print(f"Senha: {password}")
    print(f"Créditos: {creditos}")
    
    return True, password

def main():
    """Função principal para criar todos os usuários"""
    print("Iniciando criação de usuários...")
    
    # Conecta ao banco de dados
    conn = sqlite3.connect('app.db')
    
    created_users = []
    
    for user_data in USERS_TO_CREATE:
        email = user_data["email"]
        nome_completo = user_data["nome_completo"]
        
        print(f"\nProcessando usuário: {email}")
        success, password = create_user_direct(
            conn=conn,
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
    
    # Fecha a conexão
    conn.close()
    
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