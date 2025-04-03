from app.db.session import Base, engine
from app.models.user import User
from app.models.chat_session import ChatSession, ChatMessage

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 