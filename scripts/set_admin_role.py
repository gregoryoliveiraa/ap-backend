import sys
import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User

# Add parent directory to path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def set_user_as_admin(email: str):
    """Set a user as admin by email address"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"No user found with email: {email}")
            return False
        
        # Set user role to admin
        user.role = "admin"
        db.add(user)
        db.commit()
        
        print(f"User {user.nome_completo} ({email}) has been set as admin.")
        return True
    except Exception as e:
        print(f"Error setting user as admin: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python set_admin_role.py user@email.com")
        sys.exit(1)
    
    email = sys.argv[1]
    success = set_user_as_admin(email)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1) 