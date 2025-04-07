#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from passlib.context import CryptContext
import secrets
import string

# Lista de emails para corrigir
USERS_TO_FIX = [
    "sidarta.martins@gmail.com",
    "gregory.oliveiraa@hotmail.com",
    "djalmaborgesmartins@gmail.com",
    "pagotto@freitasleite.com.br",
    "leayassuda@gmail.com",
    "righettimirela@gmail.com",
]

# Configuração para senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_simple_password(length=8):
    """Gera uma senha mais simples para ser mais fácil de usar"""
    # Somente letras e números para evitar problemas com caracteres especiais
    characters = string.ascii_letters + string.digits 
    return ''.join(secrets.choice(characters) for _ in range(length))

def fix_user_password(conn, email):
    """Corrige a senha de um usuário"""
    
    cursor = conn.cursor()
    
    # Verifica se o usuário existe
    cursor.execute("SELECT id, nome_completo FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        print(f"Usuário com email {email} não encontrado!")
        return None
    
    user_id, nome_completo = user
    
    # Gera uma nova senha simples
    new_password = generate_simple_password()
    
    # Gera o hash da senha
    hashed_password = pwd_context.hash(new_password)
    
    # Atualiza a senha no banco de dados
    cursor.execute(
        "UPDATE users SET hashed_password = ? WHERE id = ?",
        (hashed_password, user_id)
    )
    
    conn.commit()
    print(f"Senha atualizada com sucesso para {email}!")
    print(f"Nome: {nome_completo}")
    print(f"Nova senha: {new_password}")
    
    return {
        "email": email,
        "nome_completo": nome_completo,
        "senha": new_password
    }

def main():
    """Função principal para corrigir senhas dos usuários"""
    print("Iniciando correção de senhas...")
    
    # Conecta ao banco de dados
    conn = sqlite3.connect('app.db')
    
    fixed_users = []
    
    for email in USERS_TO_FIX:
        print(f"\nProcessando usuário: {email}")
        user_info = fix_user_password(conn=conn, email=email)
        
        if user_info:
            fixed_users.append(user_info)
    
    # Fecha a conexão
    conn.close()
    
    # Exibe resumo dos usuários corrigidos
    if fixed_users:
        print("\n=== RESUMO DOS USUÁRIOS COM SENHAS CORRIGIDAS ===")
        for user in fixed_users:
            print(f"Email: {user['email']}")
            print(f"Nome: {user['nome_completo']}")
            print(f"Nova senha: {user['senha']}")
            print("-" * 40)
    
    print("\nProcesso concluído!")

if __name__ == "__main__":
    main() 