# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, UUID4
from datetime import datetime

# Esquema base para usuário
class UserBase(BaseModel):
    email: EmailStr
    name: str
    oab_number: Optional[str] = None

# Esquema para criação de usuário (registro)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Esquema para atualização de usuário
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    oab_number: Optional[str] = None

# Esquema para login de usuário
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Esquema para resposta de token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Esquema para conteúdo do token
class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Esquema para resposta de usuário
class UserResponse(UserBase):
    id: UUID4
    oab_verified: bool
    credits: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Esquema para verificação de OAB
class OABVerification(BaseModel):
    oab_number: str