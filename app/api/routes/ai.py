# app/api/routes/ai.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatHistory
from app.services.ai_service import AIService
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    JurisprudenceSearchRequest,
    JurisprudenceSearchResponse,
    CreditsResponse,
    ChatMessage
)
import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Envia uma mensagem para a IA e obtém uma resposta.
    """
    # Verifica se o usuário tem créditos suficientes
    if current_user.credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem créditos suficientes para usar esta funcionalidade"
        )
    
    # Obtém o histórico da conversa se existir
    history = []
    if request.conversation_id:
        chat_history = db.query(ChatHistory).filter(
            ChatHistory.id == request.conversation_id,
            ChatHistory.user_id == current_user.id
        ).first()
        
        if chat_history:
            history = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in chat_history.messages]
    
    # Envia a mensagem para a IA
    ai_response = await AIService.chat(request.message, history)
    
    # Subtrai créditos do usuário (1 crédito por mensagem)
    current_user.credits -= 1
    db.commit()
    
    # Salva a conversa no histórico
    chat_id = None
    if request.conversation_id:
        chat_history = db.query(ChatHistory).filter(
            ChatHistory.id == request.conversation_id,
            ChatHistory.user_id == current_user.id
        ).first()
        
        if chat_history:
            chat_history.messages.append({"role": "user", "content": request.message})
            chat_history.messages.append({"role": "assistant", "content": ai_response})
            db.commit()
            chat_id = chat_history.id
    else:
        # Cria um novo histórico
        new_chat = ChatHistory(
            id=uuid.uuid4(),
            user_id=current_user.id,
            messages=[
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": ai_response}
            ]
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)
        chat_id = new_chat.id
    
    return {
        "response": ai_response,
        "conversation_id": chat_id,
        "credits_remaining": current_user.credits
    }

@router.post("/analyze-document", response_model=DocumentAnalysisResponse)
async def analyze_document(
    request: DocumentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analisa um documento jurídico usando a IA.
    """
    # Verifica se o usuário tem créditos suficientes (5 créditos para análise)
    if current_user.credits < 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem créditos suficientes para usar esta funcionalidade"
        )
    
    # Envia o documento para análise pela IA
    analysis = await AIService.analyze_document(request.document_text)
    
    # Subtrai créditos do usuário
    current_user.credits -= 5
    db.commit()
    
    return {
        "analysis": analysis,
        "credits_remaining": current_user.credits
    }

@router.post("/generate-document", response_model=DocumentGenerationResponse)
async def generate_document(
    request: DocumentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Gera um documento jurídico usando a IA.
    """
    # Verifica se o usuário tem créditos suficientes (10 créditos para geração)
    if current_user.credits < 10:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem créditos suficientes para usar esta funcionalidade"
        )
    
    # Gera o documento usando a IA
    document = await AIService.generate_document(request.document_type, request.parameters)
    
    # Subtrai créditos do usuário
    current_user.credits -= 10
    db.commit()
    
    return {
        "document": document,
        "credits_remaining": current_user.credits
    }

@router.post("/search-jurisprudence", response_model=JurisprudenceSearchResponse)
async def search_jurisprudence(
    request: JurisprudenceSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Pesquisa jurisprudência relacionada à consulta.
    """
    # Verifica se o usuário tem créditos suficientes (3 créditos para pesquisa)
    if current_user.credits < 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem créditos suficientes para usar esta funcionalidade"
        )
    
    # Pesquisa jurisprudência com auxílio da IA
    results = await AIService.search_jurisprudence(request.query, request.filters)
    
    # Subtrai créditos do usuário
    current_user.credits -= 3
    db.commit()
    
    return {
        "results": results,
        "credits_remaining": current_user.credits
    }

@router.get("/credits", response_model=CreditsResponse)
async def get_credits(current_user: User = Depends(get_current_user)) -> Any:
    """
    Obtém o saldo de créditos do usuário.
    """
    return {
        "credits": current_user.credits
    }