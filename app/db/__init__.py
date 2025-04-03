from .base_class import Base
from .session import SessionLocal, engine

__all__ = ["Base", "SessionLocal", "engine"]

# Create all tables
Base.metadata.create_all(bind=engine)

