from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str
    type: str  # 'info', 'warning', 'success', 'error'
    target_users: Optional[List[str]] = None  # List of user IDs
    target_role: Optional[str] = None  # Target a specific role
    target_all: Optional[bool] = False  # Send to all users
    expiry_date: Optional[datetime] = None  # When notification expires
    action_link: Optional[str] = None  # Optional URL for action


class NotificationCreate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: str
    created_at: datetime
    read: Optional[bool] = False
    
    class Config:
        from_attributes = True 