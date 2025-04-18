from pydantic import BaseModel, UUID4, field_validator
from typing import Optional, List, Any
from datetime import datetime

# Helper validator para converter "" para None em campos opcionais
def empty_str_to_none(value: Any) -> Any:
    if value == "":
        return None
    return value

# Campos base de uma notificação
class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = 'info'
    target_all: bool = False
    target_role: Optional[str] = None
    target_users: Optional[List[UUID4]] = None
    expiry_date: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    action_link: Optional[str] = None

    # Validadores Pydantic V2
    _normalize_expiry = field_validator('expiry_date', mode='before')(empty_str_to_none)
    _normalize_scheduled = field_validator('scheduled_at', mode='before')(empty_str_to_none)

# Schema para criar uma notificação (recebido via API)
class NotificationCreate(NotificationBase):
    pass

# Schema para atualizar uma notificação (potencialmente útil no futuro)
# class NotificationUpdate(NotificationBase):
#     title: Optional[str] = None
#     message: Optional[str] = None
#     type: Optional[str] = None
#     target_all: Optional[bool] = None
#     expiry_date: Optional[datetime] = None
#     action_link: Optional[str] = None

# Schema para retornar uma notificação via API (inclui campos gerados)
class NotificationRead(NotificationBase):
    id: UUID4
    created_at: datetime
    read: Optional[bool] = None
    
    class Config:
        # Atualizado de orm_mode para from_attributes (Pydantic V2+)
        from_attributes = True 