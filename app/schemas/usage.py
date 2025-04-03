from pydantic import BaseModel
from typing import List, Dict, Any
from .payment import PaymentHistory

class ChatHistoryItem(BaseModel):
    id: str
    date: str
    tokensUsed: int

class DocumentHistoryItem(BaseModel):
    id: str
    date: str
    tokensUsed: int
    documentType: str

class UsageResponse(BaseModel):
    totalTokens: int
    totalDocuments: int
    availableTokens: int
    chatHistory: List[ChatHistoryItem]
    documentHistory: List[DocumentHistoryItem]
    payment_history: List[PaymentHistory]

    class Config:
        from_attributes = True 