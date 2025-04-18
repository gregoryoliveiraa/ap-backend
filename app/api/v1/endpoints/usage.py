from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.usage import Usage
from app.models.payment import Payment
from app.schemas.usage import UsageResponse
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter()

# Taxa de conversão: quantos tokens equivalem a 1 crédito
TOKENS_POR_CREDITO = 20

# Função para calcular quantos créditos serão consumidos por um determinado número de tokens
def calcular_creditos_consumidos(tokens_usados: int) -> int:
    """
    Calcula quantos créditos serão consumidos por um determinado número de tokens.
    Atualmente, cada 20 tokens consomem 1 crédito.
    """
    return max(1, int(tokens_usados / TOKENS_POR_CREDITO))

class AddCreditsRequest(BaseModel):
    amount: float
    payment_method: str
    card_data: Optional[dict] = None

@router.get("")
@router.get("/")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for the current user
    """
    try:
        # Get or create usage record for the user
        usage = db.query(Usage).filter(Usage.user_id == current_user.id).first()
        if not usage:
            usage = Usage(user_id=current_user.id, 
                         total_tokens=0,
                         total_documents=0,
                         available_tokens=0,
                         document_history=[])
            db.add(usage)
            db.commit()
            db.refresh(usage)
        
        # Log para debug
        print(f"Usage record from database: {usage.id}, total_tokens={usage.total_tokens}")
        
        # Se o total de tokens no registro de uso for zero, calcular a partir das mensagens
        total_tokens = usage.total_tokens
        if total_tokens == 0:
            # Calcular o total de tokens usados a partir das mensagens
            tokens_result = db.query(func.sum(ChatMessage.tokens_used)).filter(
                ChatMessage.tokens_used > 0,
                ChatMessage.role == "assistant"
            ).join(
                ChatSession,
                ChatMessage.session_id == ChatSession.id
            ).filter(
                ChatSession.user_id == current_user.id
            ).scalar()
            
            total_tokens = tokens_result or 0
            print(f"Calculated total tokens from messages: {total_tokens}")
            
            # Atualizar o registro de uso se o valor calculado for maior que zero
            if total_tokens > 0:
                usage.total_tokens = total_tokens
                db.commit()
                db.refresh(usage)

        # Get chat history
        chat_history = db.query(
            ChatMessage,
            ChatSession
        ).join(
            ChatSession,
            ChatMessage.session_id == ChatSession.id
        ).filter(
            ChatSession.user_id == current_user.id,
            ChatMessage.role == "assistant"
        ).order_by(
            ChatMessage.created_at.desc()
        ).all()

        # Get payment history
        payment_history = []  # Placeholder for payment history

        # Formatando a resposta para o formato esperado pelo frontend
        response_data = {
            "total_tokens": total_tokens,
            "total_documents": usage.total_documents if usage.total_documents is not None else 0,
            "available_tokens": current_user.creditos_disponiveis if current_user.creditos_disponiveis is not None else 0,
            "credits_remaining": current_user.creditos_disponiveis if current_user.creditos_disponiveis is not None else 0,
            "tokens_per_credit": TOKENS_POR_CREDITO,  # Adicionar taxa de conversão na resposta
            "chat_history": [
                {
                    "id": str(chat.id),
                    "created_at": chat.created_at.isoformat() if chat.created_at else datetime.now().isoformat(),
                    "tokens_used": chat.tokens_used if chat.tokens_used is not None else 0,
                    "session_title": session.title if hasattr(session, 'title') and session.title else "Conversa",
                    "provider": chat.provider if hasattr(chat, 'provider') and chat.provider else "openai"
                }
                for chat, session in chat_history
            ] if chat_history else [],
            "document_history": usage.document_history if usage.document_history else [],
            "payment_history": payment_history,
            "plan": current_user.plano if current_user.plano else "free"
        }
        
        print(f"Sending usage data: total_tokens={response_data['total_tokens']}, available_tokens={response_data['available_tokens']}, tokens_per_credit={TOKENS_POR_CREDITO}")
        return response_data
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_usage_stats: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading usage data: {str(e)}"
        )

@router.post("/credits", response_model=PaymentResponse)
async def add_credits(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    payment_data: AddCreditsRequest,
):
    """
    Add credits to the user account with payment
    """
    try:
        # Valor mínimo de compra
        if payment_data.amount < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O valor mínimo de compra é R$ 10,00",
            )
        
        # Definir quantos créditos/tokens o usuário vai receber
        # Regra: R$ 1,00 = 1 crédito = 20 tokens
        num_credits = int(payment_data.amount)
        tokens_added = num_credits * TOKENS_POR_CREDITO
        
        # Processamento do pagamento (simulação)
        # Em um ambiente real, aqui seria integrado com gateway de pagamento
        payment_status = "completed"
        card_last_digits = None
        
        if payment_data.payment_method == "credit":
            # Simulação de processamento de cartão de crédito
            if payment_data.card_data:
                # Em produção, aqui seria feita a validação e processamento real do cartão
                card_number = payment_data.card_data.get("number", "")
                if card_number:
                    card_last_digits = card_number[-4:] if len(card_number) >= 4 else None
        
        # Criar registro de pagamento
        payment = Payment(
            user_id=current_user.id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            status=payment_status,
            card_last_digits=card_last_digits,
        )
        db.add(payment)
        
        # Atualizar os créditos do usuário
        current_user.creditos_disponiveis += num_credits
        
        # Atualizar o registro de uso
        usage = db.query(Usage).filter(Usage.user_id == current_user.id).first()
        if not usage:
            usage = Usage(
                user_id=current_user.id,
                total_tokens=0,
                available_tokens=tokens_added,
                total_documents=0,
            )
            db.add(usage)
        else:
            usage.available_tokens += tokens_added
        
        db.commit()
        db.refresh(payment)
        
        return {
            "id": payment.id,
            "amount": payment.amount,
            "tokens_added": tokens_added,
            "status": payment.status,
            "created_at": payment.created_at.isoformat(),
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar pagamento: {str(e)}",
        )
