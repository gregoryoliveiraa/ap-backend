from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import SessionLocal
from app.models.user import User
from app.api.v1.schemas.user import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=not settings.TEST_MODE)


def get_db() -> Generator:
    """
    Dependency to get DB session
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get current authenticated user
    """
    # Se o modo de teste está ativado e o token não foi fornecido, retorna um usuário de teste
    if settings.TEST_MODE and token is None:
        # Verificar se existe um usuário de teste
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        # Se não existe, cria um usuário de teste
        if test_user is None:
            from datetime import datetime
            
            now = datetime.now()
            
            test_user = User(
                id="test-user-id-123456789",
                email="test@example.com",
                nome_completo="Usuário de Teste",
                hashed_password="$2b$12$testpasswordhashdummy",
                numero_oab="123456",
                estado_oab="SP",
                verificado=True,
                data_criacao=now,
                ultima_atualizacao=now,
                creditos_disponiveis=1000,
                plano="teste",
                is_active=True,
                created_at=now,
                updated_at=now
            )
            
            try:
                db.add(test_user)
                db.commit()
                db.refresh(test_user)
            except Exception as e:
                db.rollback()
                print(f"Erro ao criar usuário de teste: {str(e)}")
                # Mesmo com erro, não queremos quebrar o fluxo em modo de teste
        
        return test_user
        
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current active user
    """
    if not current_user.verificado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user
