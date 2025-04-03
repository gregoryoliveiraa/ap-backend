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
from app.models.document import Document, Template
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
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    
    return {
        "status": "success",
        "total": len(documents),
        "data": [
            {
                "id": doc.id,
                "title": doc.title,
                "document_type": doc.document_type,
                "content": doc.content[:100] + "..." if doc.content and len(doc.content) > 100 else doc.content,
                "tokens_used": doc.tokens_used,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at
            }
            for doc in documents
        ]
    }

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
            "content": document.content,
            "document_type": document.document_type,
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
        
        if "content" in document_data:
            document.content = document_data["content"]
        
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
                "content": document.content,
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
            content=document_text,
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
