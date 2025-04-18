from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    verificado: Optional[bool] = None
    numero_oab: Optional[str] = None
    estado_oab: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    nome_completo: str
    password: str
    numero_oab: Optional[str] = None
    estado_oab: Optional[str] = None
    
    @validator('numero_oab')
    def numero_oab_validation(cls, v, values):
        if v and not values.get('estado_oab'):
            raise ValueError('estado_oab is required when numero_oab is provided')
        return v


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


# Schema for password update requests
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


# Properties to return via API
class User(UserBase):
    id: str
    plano: str
    creditos_disponiveis: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    role: str = "user"

    class Config:
        from_attributes = True


# Properties shared by models stored in DB
class UserInDBBase(User):
    pass


# Properties to return via API for current user
class CurrentUser(User):
    pass


# Properties properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


# Admin-only user update schema
class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    plano: Optional[str] = None
    verificado: Optional[bool] = None
    role: Optional[str] = None
    
# Credit update schema for admin
class CreditUpdate(BaseModel):
    userId: str
    amount: int
    reason: str
