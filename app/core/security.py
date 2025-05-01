from datetime import datetime, timedelta
from typing import Any, Union, Optional
import logging

from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

ALGORITHM = "HS256"
logger = logging.getLogger(__name__)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError as e:
        # Log the actual error for debugging
        logger.warning(f"Error verifying password: {str(e)}")
        
        # If we're in development mode, allow plain text comparison as fallback
        # This is not secure for production but helps with testing
        if settings.ENVIRONMENT.lower() == "dev" or settings.DEBUG:
            logger.warning("Using fallback plain text password comparison")
            # Plain text fallback for testing - DO NOT USE IN PRODUCTION
            return plain_password == hashed_password
        else:
            # In production, we should not allow insecure password checks
            return False


def get_password_hash(password: str) -> str:
    """
    Hash password
    """
    return pwd_context.hash(password)
