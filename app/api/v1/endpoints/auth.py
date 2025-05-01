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
        logger.debug(f"Password from form: {form_data.password}")
        logger.debug(f"Stored hashed password: {user.hashed_password}")
        
        # For debugging in development environment, try direct comparison first
        if settings.ENVIRONMENT.lower() == "dev" and form_data.password == "admin" and user.email == "admin@example.com":
            logger.warning("Using development direct password check")
            is_valid = True
        else:
            # Normal password verification
            is_valid = verify_password(form_data.password, user.hashed_password)
        
        if not is_valid:
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug("Password verified, generating access token")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            str(user.id), expires_delta=access_token_expires
        )
        logger.debug("Access token generated successfully")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "nome_completo": user.nome_completo,
                "oab_number": user.oab_number,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "plan": user.plan,
                "token_credits": user.token_credits,
                "avatar_url": user.avatar_url
            }
        }
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        # Log more detailed error info
        logger.exception("Exception details:")
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
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        hashed_password=get_password_hash(user_in.password),
        oab_number=user_in.oab_number,
        phone=user_in.phone,
        is_active=True,
        is_admin=False,
        token_credits=10,  # Initial free credits
        plan="basic",
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
            
            # Obter nome do Google
            given_name = google_data.get("given_name", "")
            family_name = google_data.get("family_name", "")
            
            # Criar novo usuário
            user = UserModel(
                email=email,
                first_name=given_name,
                last_name=family_name,
                hashed_password=get_password_hash(password),
                is_active=True,
                is_admin=False,
                token_credits=10,  # Créditos iniciais
                plan="basic",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Gerar token de acesso para o usuário
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                str(user.id), expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "nome_completo": user.nome_completo,  # Usando a property para compatibilidade
                "oab_number": user.oab_number,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "plan": user.plan,
                "token_credits": user.token_credits,
                "avatar_url": user.avatar_url
            }
        }
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao comunicar com a API do Google: {str(e)}",
        )
