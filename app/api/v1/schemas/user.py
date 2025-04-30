from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    verificado: Optional[bool] = None
    numero_oab: Optional[str] = None
    estado_oab: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    first_name: str
    last_name: str
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
    is_admin: bool = False
    plan: str = "basic"
    token_credits: int = 0
    avatar_url: Optional[str] = None
    is_verified: bool = False

    @property
    def nome_completo(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""

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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    token_credits: Optional[int] = None


# Schema for credit updates
class CreditUpdate(BaseModel):
    token_credits: int
    operation: str = Field(..., description="Operation type: 'add' or 'subtract'")
    reason: Optional[str] = None
