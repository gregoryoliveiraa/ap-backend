from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class ChatMessageBase(BaseModel):
    conteudo: str
    role: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    sessao_id: int
    timestamp: datetime
    tokens_utilizados: int

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    titulo: str
    arquivado: bool = False

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: int
    usuario_id: int
    data_criacao: datetime
    ultima_mensagem: datetime
    mensagens: List[ChatMessage] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    message: str
    session_id: int
    tokens_used: int 