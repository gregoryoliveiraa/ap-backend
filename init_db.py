from app.db.base_class import Base
from app.db.session import engine
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 