# app/core/config.py
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    DEBUG: bool = True
    
    # Nome do projeto
    PROJECT_NAME: str = "Advogada Parceira API"
    ENVIRONMENT: str = "development"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    FRONTEND_URL: str = "http://localhost:3000"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/advogada_parceira")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()