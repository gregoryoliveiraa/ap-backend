from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import csv
import os
import json
from datetime import datetime
import pandas as pd
import openai
import uuid
import re
from sqlalchemy.sql import func

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.document import Document, Template, DocumentFolder
from app.core.config import settings

router = APIRouter()

# Configuração da API OpenAI
openai.api_key = settings.OPENAI_API_KEY

# Caminho para o arquivo CSV de petições (mantido para compatibilidade)
PETICOES_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "data", "peticoes.csv")

def get_template_types(db: Session):
    """
    Extrai os tipos de templates disponíveis do banco de dados
    """
    try:
        # Consulta as categorias distintas
        categorias = db.query(Template.category).distinct().all()
        categorias = [cat[0] for cat in categorias if cat[0]]
        
        # Consulta as subcategorias para cada categoria
        subcategorias = {}
        for categoria in categorias:
            subs = db.query(Template.type).filter(Template.category == categoria).distinct().all()
            subcategorias[categoria] = [sub[0] for sub in subs if sub[0]]
        
        return {
            "categorias": categorias,
            "subcategorias": subcategorias
        }
    except Exception as e:
        return {"error": f"Erro ao obter categorias: {str(e)}"}

@router.get("/")
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna todos os documentos do usuário
    """
    try:
        documents = db.query(Document).filter(Document.user_id == current_user.id).all()
        
        document_list = []
        for doc in documents:
            document_list.append({
                "id": doc.id,
                "title": doc.title,
                "document_type": doc.document_type,
                "folder_id": doc.folder_id,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at
            })
        
        return {
            "status": "success",
            "data": document_list
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter documentos: {str(e)}"
        )

@router.get("/templates/categories")
async def get_template_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna as categorias e subcategorias disponíveis para templates
    """
    result = get_template_types(db)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return {
        "status": "success",
        "data": result
    }

@router.get("/templates/{template_id}")
async def get_template_details(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de um template específico para geração de documento
    """
    try:
        # Buscar template do banco de dados
        template = db.query(Template).filter(Template.id == template_id).first()
        
        # Se não encontrou pelo ID, tenta pelo nome
        if not template:
            template = db.query(Template).filter(Template.name == template_id).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template não encontrado: {template_id}"
            )
        
        # Obter o texto do template
        template_text = template.content
        
        # Obter variáveis do campo variables se existir, ou extrair do texto
        variables = []
        if template.variables and template.variables.strip():
            try:
                variables = json.loads(template.variables)
            except json.JSONDecodeError:
                # Se não conseguir decodificar, deixa a lista vazia para extrair do texto
                pass
        
        # Se não temos variáveis, extraímos do texto como fallback
        if not variables:
            import re
            matches = re.findall(r'\[([^\]]+)\]', template_text)
            for var in matches:
                if var not in variables:
                    variables.append(var)
        
        return {
            "status": "success",
            "data": {
                "id": template.id,
                "name": template.name,
                "categoria": template.category,
                "subcategoria": template.type,
                "text": template_text,
                "variables": variables
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter detalhes do template: {str(e)}"
        )

@router.get("/templates")
async def list_templates(
    categoria: Optional[str] = None,
    subcategoria: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista os templates disponíveis com filtros opcionais e paginação
    """
    try:
        # Criar consulta base
        query = db.query(Template)
        
        # Aplicar filtros se fornecidos
        if categoria:
            query = query.filter(Template.category == categoria)
        
        if subcategoria:
            query = query.filter(Template.type == subcategoria)
        
        # Contar o total antes de aplicar paginação
        total = query.count()
        
        # Aplicar paginação
        templates_db = query.offset(skip).limit(limit).all()
        
        # Converter para o formato esperado pela API
        templates = [
            {
                "document_name": t.name,
                "subfolder_1": t.category,
                "subfolder_2": t.type,
                "subfolder_3": None,
                "id": t.id
            }
            for t in templates_db
        ]
        
        return {
            "status": "success",
            "total": total,
            "count": len(templates),
            "data": templates
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar templates: {str(e)}"
        )

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna um documento específico
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )
    
    return {
        "status": "success",
        "data": {
            "id": document.id,
            "title": document.title,
            "document_type": document.document_type,
            "folder_id": document.folder_id,
            "created_at": document.created_at,
            "updated_at": document.updated_at
        }
    }

@router.put("/{document_id}")
async def update_document(
    document_id: str,
    document_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um documento existente
    """
    try:
        # Verificar se o documento existe e pertence ao usuário atual
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado"
            )
        
        # Atualizar os campos do documento
        if "title" in document_data:
            document.title = document_data["title"]
        
        if "document_type" in document_data:
            document.document_type = document_data["document_type"]
        
        # Atualizar a data de modificação
        document.updated_at = func.now()
        
        # Salvar as alterações
        db.commit()
        db.refresh(document)
        
        return {
            "status": "success",
            "message": "Documento atualizado com sucesso",
            "data": {
                "id": document.id,
                "title": document.title,
                "document_type": document.document_type,
                "created_at": document.created_at,
                "updated_at": document.updated_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar documento: {str(e)}"
        )

@router.post("/generate")
async def generate_document(
    template_id: str = Form(...),
    variables: str = Form(...),
    formatted_title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera um documento com base em um template e valores de variáveis
    """
    try:
        # Log para debug
        print(f"Requisição de geração recebida:")
        print(f"Template ID: {template_id}")
        print(f"Variables: {variables}")
        print(f"Formatted title: {formatted_title}")
        
        # Carrega as variáveis enviadas - se for string vazia, usa um dicionário vazio
        if not variables or variables.strip() == "":
            variables_dict = {}
        else:
            try:
                variables_dict = json.loads(variables)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Erro ao decodificar variáveis JSON: {str(e)}. Recebido: {variables}"
                )
        
        # Busca o template no banco de dados
        template = db.query(Template).filter(Template.id == template_id).first()
        
        # Se não encontrou pelo ID, tenta pelo nome
        if not template:
            template = db.query(Template).filter(Template.name == template_id).first()
            
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template não encontrado: {template_id}"
            )
        
        # Obter o texto do template
        document_text = template.content
        
        # Substituir as variáveis
        for var_name, var_value in variables_dict.items():
            if var_value:  # Só substitui se houver valor
                document_text = document_text.replace(f"[{var_name}]", var_value)
        
        # Usar o título formatado se fornecido, ou criar um baseado no nome do template
        document_title = formatted_title if formatted_title else f"{template.name} - {datetime.now().strftime('%d/%m/%Y')}"
        
        # Criar um novo documento no banco de dados
        new_document = Document(
            user_id=current_user.id,
            title=document_title,
            document_type=template.category,
            tokens_used=len(document_text) // 4  # Estimativa simples
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        print(f"Documento gerado com sucesso! ID: {new_document.id}")
        
        return {
            "status": "success",
            "message": "Documento gerado com sucesso",
            "data": {
                "id": new_document.id,
                "title": new_document.title,
                "created_at": new_document.created_at,
                "document_type": new_document.document_type
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar documento: {str(e)}"
        )

@router.post("/preview")
async def preview_document(
    template_id: str = Form(...),
    variables: str = Form(...),
    formatted_title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera um preview do documento com base em um template e valores de variáveis,
    sem salvar no banco de dados
    """
    try:
        # Log para debug
        print(f"Requisição de preview recebida:")
        print(f"Template ID: {template_id}")
        print(f"Variables: {variables}")
        print(f"Formatted title: {formatted_title}")
        
        # Carrega as variáveis enviadas - se for string vazia, usa um dicionário vazio
        if not variables or variables.strip() == "":
            variables_dict = {}
        else:
            try:
                variables_dict = json.loads(variables)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Erro ao decodificar variáveis JSON: {str(e)}. Recebido: {variables}"
                )
        
        # Busca o template no banco de dados
        template = db.query(Template).filter(Template.id == template_id).first()
        
        # Se não encontrou pelo ID, tenta pelo nome
        if not template:
            template = db.query(Template).filter(Template.name == template_id).first()
            
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template não encontrado: {template_id}"
            )
        
        # Obter o texto do template
        document_text = template.content
        
        # Substituir as variáveis
        for var_name, var_value in variables_dict.items():
            if var_value:  # Só substitui se houver valor
                document_text = document_text.replace(f"[{var_name}]", var_value)
        
        # Usar o título formatado se fornecido, ou criar um baseado no nome do template
        document_title = formatted_title if formatted_title else f"{template.name} - {datetime.now().strftime('%d/%m/%Y')}"
        
        print(f"Preview gerado com sucesso!")
        
        return {
            "status": "success",
            "message": "Preview do documento gerado com sucesso",
            "data": {
                "title": document_title,
                "content": document_text,
                "document_type": template.category
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar preview do documento: {str(e)}"
        )

@router.post("/ai-complete")
async def ai_complete_document(
    request_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Usa a OpenAI para ajudar a preencher campos do documento a partir de uma descrição
    """
    try:
        # Extrair dados do corpo da requisição
        template_id = request_data.get("template_id")
        description = request_data.get("description")
        
        if not template_id or not description:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Os campos template_id e description são obrigatórios"
            )
        
        # Buscar template do banco de dados
        template = db.query(Template).filter(Template.id == template_id).first()
        
        # Se não encontrou pelo ID, tenta pelo nome
        if not template:
            template = db.query(Template).filter(Template.name == template_id).first()
            
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template não encontrado: {template_id}"
            )
        
        # Obter o texto do template
        template_text = template.content
        
        # Obter variáveis do campo variables se existir, ou extrair do texto
        variables = []
        if template.variables and template.variables.strip():
            try:
                variables = json.loads(template.variables)
            except json.JSONDecodeError:
                # Se não conseguir decodificar, deixa a lista vazia para extrair do texto
                pass
        
        # Se não temos variáveis, extraímos do texto como fallback
        if not variables:
            import re
            matches = re.findall(r'\[([^\]]+)\]', template_text)
            for var in matches:
                if var not in variables:
                    variables.append(var)
        
        # Construir o prompt para a OpenAI
        prompt = f"""
        Com base na seguinte descrição de um caso jurídico:
        
        "{description}"
        
        Por favor, forneça informações para preencher os seguintes campos de um documento jurídico do tipo {template.name}:
        
        {', '.join(variables)}
        
        Sua resposta deve estar no formato JSON com chaves correspondentes aos campos acima e valores apropriados.
        Mantenha os valores concisos e relevantes para o caso descrito. Não invente leis ou detalhes que possam prejudicar
        o processo jurídico. Use apenas informações fornecidas na descrição ou conhecimento jurídico factual.
        
        Por exemplo:
        {{
          "NOME_COMPLETO": "João da Silva",
          "NÚMERO_CPF": "123.456.789-00"
        }}
        """
        
        # Chamar a API da OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente jurídico especializado em ajudar advogados a preencher documentos legais com base em descrições de casos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extrair a resposta
        ai_suggestion = response.choices[0].message.content
        
        # Tentar fazer parse do JSON
        try:
            # Limpar a resposta para garantir que é JSON válido
            if "```json" in ai_suggestion:
                ai_suggestion = ai_suggestion.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_suggestion:
                ai_suggestion = ai_suggestion.split("```")[1].split("```")[0].strip()
            
            suggestions = json.loads(ai_suggestion)
            
            # Calcular tokens usados
            tokens_used = response.usage.total_tokens
            
            # Atualizar os créditos do usuário
            from app.api.v1.endpoints.usage import calcular_creditos_consumidos
            creditos_consumidos = calcular_creditos_consumidos(tokens_used)
            
            user = db.query(User).filter(User.id == current_user.id).first()
            if user.creditos_disponiveis < creditos_consumidos:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Créditos insuficientes para completar a operação"
                )
            
            user.creditos_disponiveis -= creditos_consumidos
            db.commit()
            
            return {
                "status": "success",
                "message": "Sugestões geradas com sucesso",
                "data": {
                    "suggestions": suggestions,
                    "tokens_used": tokens_used,
                    "credits_used": creditos_consumidos
                }
            }
        except json.JSONDecodeError:
            # Se o parse falhar, retorna o texto bruto
            return {
                "status": "warning",
                "message": "Não foi possível formatar as sugestões como JSON",
                "data": {
                    "raw_suggestion": ai_suggestion,
                    "variables": variables
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar sugestões com IA: {str(e)}"
        )

@router.get("/folders")
async def get_user_folders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna todas as pastas do usuário
    """
    try:
        folders = db.query(DocumentFolder).filter(DocumentFolder.user_id == current_user.id).all()
        
        folders_data = []
        for folder in folders:
            folders_data.append({
                "id": folder.id,
                "name": folder.name,
                "parent_id": folder.parent_id,
                "created_at": folder.created_at,
                "updated_at": folder.updated_at
            })
        
        return {
            "status": "success",
            "data": folders_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pastas: {str(e)}"
        )

@router.post("/folders")
async def create_folder(
    folder_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova pasta para o usuário
    """
    try:
        # Validar entrada
        if "name" not in folder_data or not folder_data["name"].strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome da pasta é obrigatório"
            )
        
        # Criar pasta
        new_folder = DocumentFolder(
            user_id=current_user.id,
            name=folder_data["name"],
            parent_id=folder_data.get("parent_id")
        )
        
        # Verificar se parent_id existe (se fornecido)
        if new_folder.parent_id:
            parent = db.query(DocumentFolder).filter(
                DocumentFolder.id == new_folder.parent_id,
                DocumentFolder.user_id == current_user.id
            ).first()
            
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pasta pai não encontrada"
                )
        
        db.add(new_folder)
        db.commit()
        db.refresh(new_folder)
        
        return {
            "status": "success",
            "data": {
                "id": new_folder.id,
                "name": new_folder.name,
                "parent_id": new_folder.parent_id,
                "created_at": new_folder.created_at,
                "updated_at": new_folder.updated_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar pasta: {str(e)}"
        )

@router.put("/folders/{folder_id}")
async def update_folder(
    folder_id: str,
    folder_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma pasta existente
    """
    try:
        # Buscar pasta
        folder = db.query(DocumentFolder).filter(
            DocumentFolder.id == folder_id,
            DocumentFolder.user_id == current_user.id
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pasta não encontrada"
            )
        
        # Validar e atualizar nome
        if "name" in folder_data and folder_data["name"].strip():
            folder.name = folder_data["name"]
        
        # Validar e atualizar pasta pai
        if "parent_id" in folder_data:
            # Não permitir pasta ser pai dela mesma
            if folder_data["parent_id"] == folder.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Pasta não pode ser pai dela mesma"
                )
            
            # Verificar se pasta pai existe
            if folder_data["parent_id"]:
                parent = db.query(DocumentFolder).filter(
                    DocumentFolder.id == folder_data["parent_id"],
                    DocumentFolder.user_id == current_user.id
                ).first()
                
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Pasta pai não encontrada"
                    )
                
                # Verificar ciclo de pastas
                current_parent = parent
                while current_parent:
                    if current_parent.id == folder.id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Operação criaria um ciclo de pastas"
                        )
                    
                    if not current_parent.parent_id:
                        break
                    
                    current_parent = db.query(DocumentFolder).filter(
                        DocumentFolder.id == current_parent.parent_id
                    ).first()
            
            folder.parent_id = folder_data["parent_id"]
        
        db.commit()
        db.refresh(folder)
        
        return {
            "status": "success",
            "data": {
                "id": folder.id,
                "name": folder.name,
                "parent_id": folder.parent_id,
                "created_at": folder.created_at,
                "updated_at": folder.updated_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar pasta: {str(e)}"
        )

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exclui uma pasta e move seus documentos para a raiz
    """
    try:
        # Buscar pasta
        folder = db.query(DocumentFolder).filter(
            DocumentFolder.id == folder_id,
            DocumentFolder.user_id == current_user.id
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pasta não encontrada"
            )
        
        # Mover documentos para a raiz
        documents = db.query(Document).filter(
            Document.folder_id == folder_id,
            Document.user_id == current_user.id
        ).all()
        
        for doc in documents:
            doc.folder_id = None
        
        # Atualizar pastas filhas para apontar para o pai da pasta a ser excluída
        children = db.query(DocumentFolder).filter(
            DocumentFolder.parent_id == folder_id,
            DocumentFolder.user_id == current_user.id
        ).all()
        
        for child in children:
            child.parent_id = folder.parent_id
        
        # Excluir pasta
        db.delete(folder)
        db.commit()
        
        return {
            "status": "success",
            "message": "Pasta excluída com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir pasta: {str(e)}"
        )

@router.put("/{document_id}/move")
async def move_document(
    document_id: str,
    move_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Move um documento para outra pasta
    """
    try:
        # Buscar documento
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado"
            )
        
        # Verificar pasta destino (se não for nulo)
        folder_id = move_data.get("folder_id")
        if folder_id:
            folder = db.query(DocumentFolder).filter(
                DocumentFolder.id == folder_id,
                DocumentFolder.user_id == current_user.id
            ).first()
            
            if not folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pasta destino não encontrada"
                )
        
        # Mover documento
        document.folder_id = folder_id
        db.commit()
        db.refresh(document)
        
        return {
            "status": "success",
            "data": {
                "id": document.id,
                "title": document.title,
                "folder_id": document.folder_id,
                "created_at": document.created_at,
                "updated_at": document.updated_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao mover documento: {str(e)}"
        )

@router.post("/templates/import")
async def import_templates_from_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Importa templates do arquivo CSV de petições para o banco de dados
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem importar templates"
        )
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(PETICOES_CSV_PATH):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo CSV de petições não encontrado"
            )
        
        # Carregar arquivo CSV usando pandas
        df = pd.read_csv(PETICOES_CSV_PATH, low_memory=False)
        
        # Colunas esperadas
        expected_columns = ["ID", "NOME_DOCUMENTO", "SUBFOLDER_1", "SUBFOLDER_2", "TEXTO"]
        
        # Verificar se as colunas existem
        for col in expected_columns:
            if col not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Coluna obrigatória '{col}' não encontrada no CSV"
                )
        
        # Contar templates importados
        count = 0
        
        # Iterar sobre as linhas e criar templates
        for _, row in df.iterrows():
            if not row["NOME_DOCUMENTO"] or not row["TEXTO"]:
                continue
            
            # Verificar se o template já existe pelo ID
            existing = db.query(Template).filter(Template.name == row["ID"]).first()
            
            if existing:
                # Atualizar template existente
                existing.name = row["NOME_DOCUMENTO"]
                existing.content = row["TEXTO"]
                existing.category = row["SUBFOLDER_1"] if not pd.isna(row["SUBFOLDER_1"]) else "Sem Categoria"
                existing.type = row["SUBFOLDER_2"] if not pd.isna(row["SUBFOLDER_2"]) else "Geral"
                
                # Extrair variáveis do texto
                variables = []
                matches = re.findall(r'\[([^\]]+)\]', row["TEXTO"])
                if matches:
                    variables = list(set(matches))  # Remove duplicados
                
                existing.variables = json.dumps(variables) if variables else None
                existing.updated_at = func.now()
            else:
                # Criar novo template
                category = row["SUBFOLDER_1"] if not pd.isna(row["SUBFOLDER_1"]) else "Sem Categoria"
                template_type = row["SUBFOLDER_2"] if not pd.isna(row["SUBFOLDER_2"]) else "Geral"
                
                # Extrair variáveis do texto
                variables = []
                matches = re.findall(r'\[([^\]]+)\]', row["TEXTO"])
                if matches:
                    variables = list(set(matches))  # Remove duplicados
                
                new_template = Template(
                    name=row["NOME_DOCUMENTO"],
                    content=row["TEXTO"],
                    category=category,
                    type=template_type,
                    variables=json.dumps(variables) if variables else None
                )
                
                db.add(new_template)
            
            count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Importação concluída com sucesso",
            "data": {
                "count": count
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao importar templates: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exclui um documento
    """
    try:
        # Buscar documento
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado"
            )
        
        # Excluir documento
        db.delete(document)
        db.commit()
        
        return {
            "status": "success",
            "message": "Documento excluído com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir documento: {str(e)}"
        )
