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
            try:
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
            except Exception as inner_e:
                print(f"Error calculating tokens from messages: {str(inner_e)}")
                # Continue with zero tokens if calculation fails

        # Get chat history - with error handling
        chat_history = []
        try:
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
        except Exception as chat_e:
            print(f"Error fetching chat history: {str(chat_e)}")
            # Continue with empty chat history if query fails

        # Get payment history - with error handling
        payment_history = []
        try:
            payment_history = db.query(Payment).filter(
                Payment.user_id == current_user.id
            ).order_by(
                Payment.created_at.desc()
            ).all()
        except Exception as payment_e:
            print(f"Error fetching payment history: {str(payment_e)}")
            # Continue with empty payment history if query fails

        # Obter créditos disponíveis do usuário com segurança
        available_credits = 0
        try:
            available_credits = getattr(current_user, 'available_credits', 0) or 0
        except Exception as credit_e:
            print(f"Error getting available credits: {str(credit_e)}")

        # Formatando a resposta para o formato esperado pelo frontend
        response_data = {
            "total_tokens": total_tokens,
            "total_documents": usage.total_documents if usage.total_documents is not None else 0,
            "available_tokens": available_credits,
            "credits_remaining": available_credits,
            "tokens_per_credit": TOKENS_POR_CREDITO,  # Adicionar taxa de conversão na resposta
            "chat_history": [],
            "document_history": [],
            "payment_history": []
        }

        # Adicionar histórico de chat com tratamento de erro para cada item
        if chat_history:
            chat_history_list = []
            for chat, session in chat_history:
                try:
                    chat_history_list.append({
                        "id": str(chat.id),
                        "created_at": chat.created_at.isoformat() if hasattr(chat, 'created_at') and chat.created_at else datetime.now().isoformat(),
                        "tokens_used": chat.tokens_used if hasattr(chat, 'tokens_used') and chat.tokens_used is not None else 0,
                        "session_title": session.title if hasattr(session, 'title') and session.title else "Conversa",
                        "provider": chat.provider if hasattr(chat, 'provider') and chat.provider else "openai"
                    })
                except Exception as item_e:
                    print(f"Error processing chat history item: {str(item_e)}")
                    continue
            response_data["chat_history"] = chat_history_list

        # Adicionar histórico de documentos
        if hasattr(usage, 'document_history') and usage.document_history:
            response_data["document_history"] = usage.document_history

        # Adicionar histórico de pagamentos com tratamento de erro para cada item
        if payment_history:
            payment_history_list = []
            for payment in payment_history:
                try:
                    payment_history_list.append({
                        "id": str(payment.id),
                        "created_at": payment.created_at.isoformat() if hasattr(payment, 'created_at') and payment.created_at else datetime.now().isoformat(),
                        "amount": payment.amount if hasattr(payment, 'amount') else 0,
                        "payment_method": payment.payment_method if hasattr(payment, 'payment_method') else "unknown",
                        "status": payment.status if hasattr(payment, 'status') else "unknown",
                        "card_last_digits": payment.card_last_digits if hasattr(payment, 'card_last_digits') else None
                    })
                except Exception as item_e:
                    print(f"Error processing payment history item: {str(item_e)}")
                    continue
            response_data["payment_history"] = payment_history_list

        # Adicionar plano com tratamento de erro
        try:
            response_data["plan"] = current_user.plan if hasattr(current_user, 'plan') and current_user.plan else "basic"
        except Exception as plan_e:
            print(f"Error getting user plan: {str(plan_e)}")
            response_data["plan"] = "basic"
        
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
        
        # Atualizar os créditos do usuário com tratamento de erro
        try:
            if hasattr(current_user, 'available_credits'):
                current_credits = current_user.available_credits or 0
                current_user.available_credits = current_credits + num_credits
            else:
                print("Warning: User model does not have available_credits attribute")
                # Tenta atualizar outros campos relacionados a créditos se disponíveis
                if hasattr(current_user, 'token_credits'):
                    current_user.token_credits = (current_user.token_credits or 0) + tokens_added
        except Exception as credit_e:
            print(f"Error updating user credits: {str(credit_e)}")
            # Continuar mesmo se não conseguir atualizar os créditos
        
        # Atualizar o registro de uso
        try:
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
                # Atualizar créditos se o campo existir
                if hasattr(usage, 'available_tokens'):
                    current_tokens = usage.available_tokens or 0
                    usage.available_tokens = current_tokens + tokens_added
        except Exception as usage_e:
            print(f"Error updating usage record: {str(usage_e)}")
            # Continuar mesmo se não conseguir atualizar o registro de uso
        
        # Commit das alterações
        try:
            db.commit()
            db.refresh(payment)
        except Exception as db_e:
            db.rollback()
            print(f"Error committing payment transaction: {str(db_e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar pagamento: {str(db_e)}",
            )
        
        return {
            "id": payment.id,
            "amount": payment.amount,
            "tokens_added": tokens_added,
            "status": payment.status,
            "created_at": payment.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in add_credits: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar pagamento: {str(e)}",
        )
