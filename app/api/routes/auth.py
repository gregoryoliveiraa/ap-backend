# app/api/routes/auth.py
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    UserLogin,
    OABVerification
)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Registra um novo usuário.
    """
    # Verifica se o e-mail já está em uso
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    
    # Verifica se o número da OAB já está em uso
    if user_in.oab_number:
        oab_user = db.query(User).filter(User.oab_number == user_in.oab_number).first()
        if oab_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número da OAB já está em uso"
            )
    
    # Cria um novo usuário
    user = User(
        email=user_in.email,
        name=user_in.name,
        password=get_password_hash(user_in.password),
        oab_number=user_in.oab_number,
        oab_verified=False,
        credits=100  # Créditos iniciais
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 token para login.
    """
    # Busca o usuário pelo e-mail
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verifica se o usuário existe e a senha está correta
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    # Cria o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login/alt", response_model=dict)
async def login_alt(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login alternativo (não OAuth2) para uso em frontend.
    """
    # Busca o usuário pelo e-mail
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # Verifica se o usuário existe e a senha está correta
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Verifica se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    # Cria o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "message": "Login realizado com sucesso",
        "token": access_token,
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "oab_number": user.oab_number,
            "oab_verified": user.oab_verified,
            "credits": user.credits
        }
    }

@router.post("/verify-oab", response_model=dict)
async def verify_oab(
    verification: OABVerification,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Verifica o número da OAB do usuário.
    """
    # Aqui você implementaria a verificação real da OAB
    # Por agora, vamos apenas simular uma verificação bem-sucedida
    
    # Atualiza o status de verificação do usuário
    current_user.oab_verified = True
    db.commit()
    
    return {
        "success": True,
        "message": "OAB verificada com sucesso",
        "oab_verified": True
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Obtém informações do usuário atual.
    """
    return current_user

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Renova o token JWT.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(current_user.id), expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }