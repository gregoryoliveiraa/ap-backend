# app/schemas/ai.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4

# Esquema para mensagem de chat
class ChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    content: str

# Esquema para solicitação de chat
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID4] = None

# Esquema para resposta de chat
class ChatResponse(BaseModel):
    response: str
    conversation_id: UUID4
    credits_remaining: int

# Esquema para histórico de chat
class ChatHistoryBase(BaseModel):
    title: Optional[str] = None
    messages: List[ChatMessage]

# Esquema para criação de histórico de chat
class ChatHistoryCreate(ChatHistoryBase):
    pass

# Esquema para resposta de histórico de chat
class ChatHistoryResponse(ChatHistoryBase):
    id: UUID4
    user_id: UUID4
    created_at: str
    last_updated: str
    
    class Config:
        from_attributes = True

# Esquema para solicitação de análise de documento
class DocumentAnalysisRequest(BaseModel):
    document_text: str

# Esquema para resposta de análise de documento
class DocumentAnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    credits_remaining: int

# Esquema para solicitação de geração de documento
class DocumentGenerationRequest(BaseModel):
    document_type: str
    parameters: Dict[str, Any]

# Esquema para resposta de geração de documento
class DocumentGenerationResponse(BaseModel):
    document: str
    credits_remaining: int

# Esquema para solicitação de pesquisa de jurisprudência
class JurisprudenceSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None

# Esquema para resposta de pesquisa de jurisprudência
class JurisprudenceSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    credits_remaining: int

# Esquema para resposta de créditos
class CreditsResponse(BaseModel):
    credits: int