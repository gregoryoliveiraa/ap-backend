from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    nome_completo: str
    numero_oab: Optional[str] = None
    estado_oab: Optional[str] = None

class UserCreate(UserBase):
    senha: str

class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    numero_oab: Optional[str] = None
    estado_oab: Optional[str] = None
    senha: Optional[str] = None

class UserInDB(UserBase):
    id: int
    verificado: bool
    data_criacao: datetime
    ultima_atualizacao: datetime
    creditos_disponiveis: int
    plano: str

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 