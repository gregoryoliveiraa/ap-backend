from app.db.base_class import Base
from app.db.session import engine

# Import all models here in the correct order to handle dependencies
from app.models.user import User  # User should be first as other models depend on it
from app.models.usage import Usage  # Changed from usage_tracking import ApiUsage
from app.models.payment import Payment
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.document import Document, Template, DocumentTemplate, LegalThesis, GeneratedDocument, DocumentThesisAssociation
from app.models.notification import Notification

def init_db() -> None:
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine) 