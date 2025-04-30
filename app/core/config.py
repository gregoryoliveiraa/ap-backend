from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any, List, Union
from pydantic import AnyHttpUrl, field_validator
import secrets
from pathlib import Path
import json
from datetime import datetime, timedelta


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='allow',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )
    
    PROJECT_NAME: str = "API Advogada Parceira"
    API_TITLE: str = "Advogada Parceira API"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "2.1.8"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"  # Algorithm for JWT token generation
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",      # Frontend development
        "http://127.0.0.1:3000",      # Frontend development alternative
        "http://localhost:8000",      # Backend development
        "http://127.0.0.1:8000",      # Backend development alternative
        "https://app.advogadaparceira.com.br",     # Production frontend
        "https://www.app.advogadaparceira.com.br", # Production frontend with www
        "https://api.advogadaparceira.com.br",     # Production backend
    ]

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v.startswith("["):
                return [i.strip() for i in v.split(",")]
            return eval(v)
        return v

    # Database Configuration
    DATABASE_URL: str
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Settings
    ANTHROPIC_API_KEY: str = "your-anthropic-key"
    OPENAI_API_KEY: str = "your-openai-key"
    DEEPSEEK_API_KEY: str = "your-deepseek-key"
    DEFAULT_MODEL_NAME: str = "gpt-4"
    FALLBACK_MODEL_NAME: str = "gpt-3.5-turbo"
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_STORAGE_BUCKET_NAME: str = "advogada-parceira"
    AWS_S3_REGION_NAME: str = "us-east-1"
    
    # Environment
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True
    
    # Testing mode - quando True, permite acesso a endpoints sem autenticação
    TEST_MODE: bool = True

    # User Management
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"
    ADMIN_TOKEN: str = "12345"

    # SMTP Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Sentry Configuration
    SENTRY_DSN: Optional[str] = None


settings = Settings()
