from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List, Union
from pydantic import AnyHttpUrl, validator
import secrets
from pathlib import Path
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "API Advogada Parceira"
    API_TITLE: str = "API Advogada Parceira"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "2.1.8"
    SECRET_KEY: str = "your-secret-key-123"  # Change in production
    ALGORITHM: str = "HS256"  # Algorithm for JWT token generation
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://app.advogadaparceira.com.br",
        "https://www.app.advogadaparceira.com.br",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str):
            if v.startswith("["):
                parsed = json.loads(v)
                return list(dict.fromkeys(parsed))  # Remove duplicates
            # Split by comma, strip whitespace, and remove duplicates
            origins = [i.strip() for i in v.split(",")]
            return list(dict.fromkeys(origins))  # Remove duplicates while preserving order
        elif isinstance(v, list):
            # Remove duplicates while preserving order
            return list(dict.fromkeys(v))
        return v

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./app.db"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
