from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash

# Create engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Check if admin user already exists
    admin_user = db.query(User).filter(User.email == "admin@advogadaparceira.com.br").first()
    if admin_user:
        print("Admin user already exists")
    else:
        # Create admin user
        admin_user = User(
            email="admin@advogadaparceira.com.br",
            first_name="Admin",
            last_name="User",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_admin=True,
            token_credits=1000,
            plan="admin"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Admin user created successfully with email: {admin_user.email}")
finally:
    db.close() 