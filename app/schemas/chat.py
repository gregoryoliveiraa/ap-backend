from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class ChatMessageBase(BaseModel):
    content: str
    role: str = "user"
    tokens_used: int = 0
    provider: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    session_id: str

class ChatMessage(ChatMessageBase):
    id: str
    session_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: Optional[str] = None
    archived: bool = False

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[datetime] = None
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: str
    provider: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    tokens_used: int 