from passlib.context import CryptContext
from sqlalchemy import create_engine
from datetime import datetime
from app.models.user import User
from app.db.session import Base

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create database connection
engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(bind=engine)

# Admin user data
email = "admin@example.com"
password = "admin123"
nome_completo = "Administrador"

# Generate password hash
senha_hash = pwd_context.hash(password)

# Insert admin user
from sqlalchemy.orm import Session
with Session(engine) as session:
    admin_user = User(
        email=email,
        nome_completo=nome_completo,
        senha_hash=senha_hash,
        verificado=True,
        creditos_disponiveis=1000,
        plano="admin",
        data_criacao=datetime.utcnow(),
        ultima_atualizacao=datetime.utcnow()
    )
    session.add(admin_user)
    session.commit()

print(f"Admin user created successfully with email: {email} and password: {password}") 