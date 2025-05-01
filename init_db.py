from app.db.base_class import Base
from app.db.session import engine

def init_db() -> None:
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db() 