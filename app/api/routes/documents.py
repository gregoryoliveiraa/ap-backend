# app/api/routes/documents.py
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    PaginatedDocumentResponse
)

router = APIRouter()

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Cria um novo documento.
    """
    document = Document(
        id=uuid.uuid4(),
        title=document_in.title,
        content=document_in.content,
        document_type=document_in.document_type,
        tags=document_in.tags if document_in.tags else [],
        created_by=current_user.id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document

@router.get("/", response_model=PaginatedDocumentResponse)
async def get_documents(
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    doc_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtém os documentos do usuário com paginação e filtros.
    """
    # Base da query
    query = db.query(Document).filter(Document.created_by == current_user.id)
    
    # Adiciona filtros se fornecidos
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Document.title.ilike(search_term)) |
            (Document.content.ilike(search_term))
        )
    
    if doc_type:
        query = query.filter(Document.document_type == doc_type)
    
    # Total de documentos
    total = query.count()
    
    # Paginação
    skip = (page - 1) * size
    query = query.order_by(Document.created_at.desc()).offset(skip).limit(size)
    
    # Executa a query
    documents = query.all()
    
    return {
        "items": documents,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size  # Calcula número total de páginas
    }

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtém um documento específico pelo ID.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.created_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )
    
    return document

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    document_in: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Atualiza um documento existente.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.created_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado ou você não tem permissão para editá-lo"
        )
    
    # Atualiza os campos fornecidos
    update_data = document_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Exclui um documento.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.created_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado ou você não tem permissão para excluí-lo"
        )
    
    db.delete(document)
    db.commit()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    document_type: str = Form("uploaded"),
    tags: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Faz upload de um documento.
    """
    content = await file.read()
    content_str = content.decode("utf-8")
    
    # Processa as tags
    tags_list = []
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",")]
    
    document = Document(
        id=uuid.uuid4(),
        title=title if title else file.filename,
        content=content_str,
        document_type=document_type,
        tags=tags_list,
        created_by=current_user.id,
        file_name=file.filename,
        file_type=file.content_type
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document

@router.get("/templates", response_model=List[dict])
async def get_document_templates(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obtém os templates de documentos disponíveis.
    """
    # Aqui você implementaria a lógica para obter templates de documentos
    # Por enquanto, retornamos alguns templates de exemplo
    templates = [
        {
            "id": "petição-inicial",
            "name": "Petição Inicial",
            "description": "Modelo de petição inicial para processos cíveis",
            "parameters": ["juízo", "autor", "réu", "fatos", "direito", "pedidos"]
        },
        {
            "id": "contrato-prestação-serviços",
            "name": "Contrato de Prestação de Serviços",
            "description": "Modelo de contrato de prestação de serviços",
            "parameters": ["contratante", "contratado", "objeto", "valor", "prazo", "condições"]
        },
        {
            "id": "procuração",
            "name": "Procuração",
            "description": "Modelo de procuração para representação legal",
            "parameters": ["outorgante", "outorgado", "poderes", "finalidade"]
        }
    ]
    
    return templates