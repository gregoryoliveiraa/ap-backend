from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    amount: float
    payment_method: str

class PaymentCreate(PaymentBase):
    card_data: Optional[dict] = None

class PaymentResponse(BaseModel):
    id: str
    amount: float
    tokens_added: int
    status: str
    created_at: str

    class Config:
        from_attributes = True

class PaymentHistory(BaseModel):
    id: str
    date: str
    amount: float
    method: str
    status: str
    card_last_digits: Optional[str] = None

    class Config:
        from_attributes = True 