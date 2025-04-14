from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.core.security import get_password_hash, verify_password
import os
import shutil
from uuid import uuid4
from pathlib import Path

router = APIRouter()

class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    oab: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

@router.get("/me", response_model=Any)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nome_completo": f"{current_user.first_name} {current_user.last_name}",
        "firstName": current_user.first_name,
        "lastName": current_user.last_name,
        "phone": current_user.phone,
        "oab": current_user.oab,
        "verificado": current_user.is_active,
        "avatar": current_user.avatar_url,
    }

@router.put("/me", response_model=Any)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    user_in: UserUpdate,
) -> Any:
    """
    Update current user.
    """
    # Validar se email já existe (se estiver sendo atualizado)
    if user_in.email and user_in.email != current_user.email:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="O email já está em uso.",
            )
    
    # Atualizar dados do usuário
    if user_in.firstName is not None:
        current_user.first_name = user_in.firstName
    if user_in.lastName is not None:
        current_user.last_name = user_in.lastName
    if user_in.email is not None:
        current_user.email = user_in.email
    if user_in.phone is not None:
        current_user.phone = user_in.phone
    if user_in.oab is not None:
        current_user.oab = user_in.oab
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nome_completo": f"{current_user.first_name} {current_user.last_name}",
        "firstName": current_user.first_name,
        "lastName": current_user.last_name,
        "phone": current_user.phone,
        "oab": current_user.oab,
        "verificado": current_user.is_active,
        "avatar": current_user.avatar_url,
    }

@router.put("/me/password", response_model=Any)
def update_password(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    password_in: PasswordUpdate,
) -> Any:
    """
    Update current user password.
    """
    # Verificar senha atual
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Senha atual incorreta",
        )
    
    # Atualizar senha
    hashed_password = get_password_hash(password_in.new_password)
    current_user.hashed_password = hashed_password
    
    db.add(current_user)
    db.commit()
    
    return {"message": "Senha atualizada com sucesso"}

@router.post("/me/avatar", response_model=Any)
async def upload_avatar(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
) -> Any:
    """
    Upload user avatar.
    """
    # Verificar tipo de arquivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Apenas arquivos de imagem são permitidos",
        )
    
    # Verificar tamanho do arquivo (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=400,
            detail="O arquivo deve ter no máximo 5MB",
        )
    await file.seek(0)  # Reset file pointer
    
    # Criar diretório para avatares se não existir
    AVATAR_DIR = Path("app/static/avatars")
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remover avatar antigo se existir
    if current_user.avatar_url:
        old_avatar_path = AVATAR_DIR / os.path.basename(current_user.avatar_url)
        if old_avatar_path.exists():
            os.remove(old_avatar_path)
    
    # Gerar nome de arquivo único
    file_extension = os.path.splitext(file.filename)[1]
    avatar_filename = f"{current_user.id}_{uuid4().hex}{file_extension}"
    avatar_path = AVATAR_DIR / avatar_filename
    
    # Salvar arquivo
    with avatar_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Atualizar URL do avatar no banco de dados
    avatar_url = f"/static/avatars/{avatar_filename}"
    current_user.avatar_url = avatar_url
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {
        "avatar": avatar_url,
        "message": "Avatar atualizado com sucesso"
    }

@router.delete("/me/avatar", response_model=Any)
def delete_avatar(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete user avatar.
    """
    if not current_user.avatar_url:
        raise HTTPException(
            status_code=404,
            detail="Usuário não possui avatar",
        )
    
    # Remover arquivo
    AVATAR_DIR = Path("app/static/avatars")
    avatar_path = AVATAR_DIR / os.path.basename(current_user.avatar_url)
    if avatar_path.exists():
        os.remove(avatar_path)
    
    # Atualizar banco de dados
    current_user.avatar_url = None
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Avatar removido com sucesso"} 