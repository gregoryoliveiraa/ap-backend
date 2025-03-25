# app/services/document_service.py
import os
import uuid
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentService:
    @staticmethod
    async def create_document(db: Session, document_data: DocumentCreate, user_id: uuid.UUID) -> Document:
        """
        Cria um novo documento no banco de dados.
        
        Args:
            db: Sessão do banco de dados
            document_data: Dados do documento a ser criado
            user_id: ID do usuário que está criando o documento
            
        Returns:
            Objeto Document criado
        """
        document = Document(
            id=uuid.uuid4(),
            title=document_data.title,
            content=document_data.content,
            document_type=document_data.document_type,
            tags=document_data.tags if document_data.tags else [],
            created_by=user_id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
    
    @staticmethod
    async def get_user_documents(
        db: Session, 
        user_id: uuid.UUID, 
        page: int = 1, 
        size: int = 10, 
        search: Optional[str] = None, 
        doc_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtém documentos do usuário com paginação e filtros.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            page: Número da página para paginação
            size: Tamanho da página
            search: Termo de busca opcional
            doc_type: Filtro de tipo de documento opcional
            
        Returns:
            Dicionário com documentos e informações de paginação
        """
        # Base da query
        query = db.query(Document).filter(Document.created_by == user_id)
        
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
    
    @staticmethod
    async def get_document_by_id(db: Session, document_id: uuid.UUID, user_id: uuid.UUID) -> Document:
        """
        Obtém um documento específico pelo ID.
        
        Args:
            db: Sessão do banco de dados
            document_id: ID do documento
            user_id: ID do usuário para verificação de permissão
            
        Returns:
            Objeto Document
            
        Raises:
            HTTPException: Se o documento não for encontrado ou o usuário não tiver permissão
        """
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.created_by == user_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado ou você não tem permissão para acessá-lo"
            )
        
        return document
    
    @staticmethod
    async def update_document(db: Session, document_id: uuid.UUID, document_data: DocumentUpdate, user_id: uuid.UUID) -> Document:
        """
        Atualiza um documento existente.
        
        Args:
            db: Sessão do banco de dados
            document_id: ID do documento a ser atualizado
            document_data: Dados atualizados do documento
            user_id: ID do usuário para verificação de permissão
            
        Returns:
            Objeto Document atualizado
            
        Raises:
            HTTPException: Se o documento não for encontrado ou o usuário não tiver permissão
        """
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.created_by == user_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado ou você não tem permissão para editá-lo"
            )
        
        # Atualiza os campos fornecidos
        update_data = document_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        
        db.commit()
        db.refresh(document)
        
        return document
    
    @staticmethod
    async def delete_document(db: Session, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Exclui um documento.
        
        Args:
            db: Sessão do banco de dados
            document_id: ID do documento a ser excluído
            user_id: ID do usuário para verificação de permissão
            
        Raises:
            HTTPException: Se o documento não for encontrado ou o usuário não tiver permissão
        """
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.created_by == user_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado ou você não tem permissão para excluí-lo"
            )
        
        db.delete(document)
        db.commit()
    
    @staticmethod
    async def process_uploaded_file(
        file: UploadFile, 
        db: Session, 
        user_id: uuid.UUID, 
        title: Optional[str] = None,
        document_type: str = "uploaded",
        tags: Optional[str] = None
    ) -> Document:
        """
        Processa e salva um arquivo enviado.
        
        Args:
            file: Arquivo enviado
            db: Sessão do banco de dados
            user_id: ID do usuário
            title: Título opcional para o documento
            document_type: Tipo de documento
            tags: Tags separadas por vírgula (opcional)
            
        Returns:
            Objeto Document criado
        """
        try:
            # Lê o conteúdo do arquivo
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
                created_by=user_id,
                file_name=file.filename,
                file_type=file.content_type
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            return document
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar o arquivo: {str(e)}"
            )
    
    @staticmethod
    def get_document_templates() -> List[Dict[str, Any]]:
        """
        Obtém os templates de documentos disponíveis.
        
        Returns:
            Lista de templates de documentos
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
            },
            {
                "id": "contestação",
                "name": "Contestação",
                "description": "Modelo de contestação para processos cíveis",
                "parameters": ["processo", "réu", "fatos", "direito", "pedidos"]
            },
            {
                "id": "recurso-apelação",
                "name": "Recurso de Apelação",
                "description": "Modelo de recurso de apelação",
                "parameters": ["processo", "apelante", "apelado", "sentença", "razões", "pedidos"]
            }
        ]
        
        return templates