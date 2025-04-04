import argparse
from passlib.context import CryptContext
from sqlalchemy import create_engine
from datetime import datetime
from app.models.user import User
from app.db.base_class import Base
from app.db.session import engine
from sqlalchemy.orm import Session
import sys

def create_admin(email, password, nome_completo, creditos=1000, plano="admin"):
    # Create password context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Generate password hash
    senha_hash = pwd_context.hash(password)

    # Check if user already exists
    with Session(engine) as session:
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Usuário com email {email} já existe!")
            return False

        # Create admin user
        admin_user = User(
            email=email,
            nome_completo=nome_completo,
            senha_hash=senha_hash,
            verificado=True,
            creditos_disponiveis=creditos,
            plano=plano,
            data_criacao=datetime.utcnow(),
            ultima_atualizacao=datetime.utcnow()
        )
        session.add(admin_user)
        session.commit()
        print(f"Usuário administrador criado com sucesso!")
        print(f"Email: {email}")
        print(f"Senha: {password}")
        print(f"Nome: {nome_completo}")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Criar usuário administrador')
    parser.add_argument('--email', default="admin@example.com", help='Email do administrador')
    parser.add_argument('--password', default="admin123", help='Senha do administrador')
    parser.add_argument('--nome', default="Administrador", help='Nome completo do administrador')
    parser.add_argument('--creditos', default=1000, type=int, help='Quantidade de créditos')
    parser.add_argument('--plano', default="admin", help='Plano do usuário')
    
    args = parser.parse_args()
    
    success = create_admin(
        email=args.email, 
        password=args.password, 
        nome_completo=args.nome,
        creditos=args.creditos,
        plano=args.plano
    )
    
    if not success:
        sys.exit(1) 