from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.dependencies import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.api.v1.schemas.user import User, UserCreate, UserInDB
from app.models.user import User as UserModel
import requests
import secrets
import string
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/login")
async def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        logger.debug(f"Attempting login for user: {form_data.username}")
        user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
        
        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Found user: {user.email}, verifying password")
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug("Password verified, generating access token")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            user.id, expires_delta=access_token_expires
        )
        logger.debug("Access token generated successfully")
        
        return {
            "access_token": token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/register", response_model=User)
async def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user
    """
    # Check if the user with this email exists
    user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Um usuário com este email já existe no sistema",
        )
    
    # Create new user
    db_user = UserModel(
        email=user_in.email,
        nome_completo=user_in.nome_completo,
        hashed_password=get_password_hash(user_in.password),
        numero_oab=user_in.numero_oab,
        estado_oab=user_in.estado_oab,
        verificado=False,
        creditos_disponiveis=10,  # Initial free credits
        plano="gratuito",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

class GoogleToken(BaseModel):
    token: str

@router.post("/google", response_model=dict)
async def login_with_google(
    *,
    db: Session = Depends(get_db),
    token_data: GoogleToken,
) -> Any:
    """
    Authenticate and/or register user with Google
    """
    try:
        # Verificar o token com o Google
        google_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_data.token}"}
        )
        
        if google_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token do Google inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        google_data = google_response.json()
        
        # Obter dados do usuário do Google
        email = google_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email não fornecido pelo Google",
            )
        
        # Verificar se o email do usuário é verificado no Google
        if not google_data.get("email_verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email do Google não verificado",
            )
        
        # Procurar usuário existente pelo email
        user = db.query(UserModel).filter(UserModel.email == email).first()
        
        # Se o usuário não existir, criar novo com dados do Google
        if not user:
            # Gerar senha aleatória para o usuário
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(16))
            
            # Obter nome completo do Google ou usar email como fallback
            nome_completo = google_data.get("name", email.split("@")[0])
            
            # Criar novo usuário
            user = UserModel(
                email=email,
                nome_completo=nome_completo,
                hashed_password=get_password_hash(password),
                verificado=True,  # Já é verificado pelo Google
                creditos_disponiveis=10,  # Créditos iniciais
                plano="gratuito",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Gerar token de acesso para o usuário
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao comunicar com a API do Google: {str(e)}",
        )
