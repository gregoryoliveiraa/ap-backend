#!/usr/bin/env python3

from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.user import User
from tabulate import tabulate

def list_users():
    print("=== Listando usuários cadastrados ===")
    
    with Session(engine) as session:
        users = session.query(User).all()
        
        if not users:
            print("Nenhum usuário encontrado!")
            return
        
        table_data = []
        for user in users:
            # Mascarar a senha por segurança
            table_data.append([
                user.id,
                user.email,
                user.nome_completo,
                user.plano,
                "Sim" if user.verificado else "Não",
                user.creditos_disponiveis,
                user.data_criacao.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        headers = ["ID", "Email", "Nome", "Plano", "Verificado", "Créditos", "Data Criação"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"Total de usuários: {len(users)}")

if __name__ == "__main__":
    try:
        list_users()
    except Exception as e:
        print(f"Erro ao listar usuários: {e}") 