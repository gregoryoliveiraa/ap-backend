from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = "info"
    target_all: bool = False
    target_role: Optional[str] = None
    target_users: Optional[List[str]] = None
    expiry_date: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    action_link: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    id: UUID
    created_at: datetime
    read: bool = False
    
    class Config:
        orm_mode = True
        from_attributes = True 