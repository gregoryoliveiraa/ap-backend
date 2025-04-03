import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.base import init_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.document import Document, Template, DocumentTemplate, LegalThesis, GeneratedDocument, DocumentThesisAssociation
from app.models.usage import Usage
from app.models.payment import Payment
from app.core.security import get_password_hash

def create_admin_user(db: Session) -> User:
    # Check if admin user already exists
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if admin:
        print("Admin user already exists")
        return admin
    
    # Create admin user
    admin_user = User(
        email="admin@example.com",
        nome_completo="Administrator",
        hashed_password=get_password_hash("admin123"),  # Change this password in production
        verificado=True,
        creditos_disponiveis=1000,  # Give admin more credits
        plano="admin",
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print("Admin user created successfully")
    return admin_user

if __name__ == "__main__":
    # Initialize the database
    init_db()
    
    # Create admin user
    db = SessionLocal()
    try:
        create_admin_user(db)
    finally:
        db.close() 