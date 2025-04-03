from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessageBase(BaseModel):
    content: str = Field(..., description="The message content")
    role: str = Field(..., description="The role of the message sender (user/assistant/system)")


class ChatMessageCreate(ChatMessageBase):
    session_id: str
    tokens_used: Optional[int] = 0


class ChatMessage(ChatMessageBase):
    id: str
    session_id: str
    created_at: datetime
    tokens_used: Optional[int] = 0

    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    title: str = Field(default="New Chat", description="The chat session title")


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None


class ChatSession(ChatSessionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[ChatMessage]] = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message to the assistant")
    session_id: Optional[str] = Field(None, description="Session ID (None for new session)")
    session_title: Optional[str] = Field(None, description="Title for new session")
    provider: Literal["openai", "claude", "deepseek"] = Field(default="deepseek", description="The AI provider to use")


class ChatResponse(BaseModel):
    message: str = Field(..., description="The assistant's response")
    session_id: str = Field(..., description="The session ID")
    tokens_used: Optional[int] = None
    provider: Optional[str] = Field(None, description="The AI provider used")
