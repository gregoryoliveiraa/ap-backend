from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    document_type: str
    

class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None


class DocumentInDB(DocumentBase):
    id: str
    user_id: str
    tokens_used: int = 0
    folder_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Document(DocumentInDB):
    pass


class FolderBase(BaseModel):
    name: str
    parent_id: Optional[str] = None


class FolderCreate(FolderBase):
    pass


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[str] = None


class FolderInDB(FolderBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Folder(FolderInDB):
    pass


class TemplateBase(BaseModel):
    name: str
    content: str
    category: str
    type: str
    variables: Optional[str] = None
    

class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    variables: Optional[str] = None


class TemplateInDB(TemplateBase):
    id: str
    is_premium: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Template(TemplateInDB):
    pass


class MoveDocument(BaseModel):
    folder_id: Optional[str] = None
