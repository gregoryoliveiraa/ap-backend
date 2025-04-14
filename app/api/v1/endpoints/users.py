from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user, get_current_active_user
from app.api.v1.schemas.user import User, UserUpdate, UserCreate, PasswordUpdate
from app.models.user import User as UserModel
from app.core.security import get_password_hash, verify_password

router = APIRouter()


@router.get("/me", response_model=User)
async def read_user_me(
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Update current user
    """
    # Update user data
    if user_in.nome_completo:
        current_user.nome_completo = user_in.nome_completo
    if user_in.email:
        # Check if email already exists
        existing_user = db.query(UserModel).filter(
            UserModel.email == user_in.email, 
            UserModel.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        current_user.email = user_in.email
    if user_in.numero_oab:
        current_user.numero_oab = user_in.numero_oab
    if user_in.estado_oab:
        current_user.estado_oab = user_in.estado_oab
    if user_in.password:
        current_user.hashed_password = get_password_hash(user_in.password)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", response_model=dict)
async def update_password(
    *,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    password_in: PasswordUpdate,
) -> Any:
    """
    Update current user password
    """
    # Verify current password
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_in.new_password)
    
    db.add(current_user)
    db.commit()
    
    return {"message": "Senha atualizada com sucesso"}
