# app/schemas/document.py
from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime

# Esquema base para documento
class DocumentBase(BaseModel):
    title: str
    content: str
    document_type: str
    tags: Optional[List[str]] = None

# Esquema para criação de documento
class DocumentCreate(DocumentBase):
    pass

# Esquema para atualização de documento
class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None

# Esquema para resposta de documento
class DocumentResponse(DocumentBase):
    id: UUID4
    created_by: UUID4
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Esquema para resposta paginada de documentos
class PaginatedDocumentResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int