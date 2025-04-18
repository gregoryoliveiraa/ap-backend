from typing import Any, List, Dict, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from uuid import UUID
import logging

from app.api.dependencies import get_db, get_admin_user
from app.models.user import User as UserModel
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.document import Document
from app.models.payment import Payment
from app.models.usage import Usage
from app.api.v1.schemas.user import User, AdminUserUpdate, CreditUpdate
from app.models.notification import Notification as NotificationModel
from app.schemas.notification import NotificationCreate, NotificationRead
from app.crud import crud_notification

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/users", response_model=List[User])
async def get_all_users(
    db: Session = Depends(get_db),
    admin: UserModel = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all users - admin only.
    """
    try:
        users = db.query(UserModel).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        import traceback
        print(f"Error getting all users: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar usuários: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=User)
async def get_user_details(
    user_id: str,
    db: Session = Depends(get_db),
    admin: UserModel = Depends(get_admin_user),
) -> Any:
    """
    Get user details - admin only.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_in: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: UserModel = Depends(get_admin_user),
) -> Any:
    """
    Update user details - admin only.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user fields if provided
    if user_in.email is not None:
        # Check if email is unique
        existing_user = db.query(UserModel).filter(
            UserModel.email == user_in.email,
            UserModel.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user.email = user_in.email
    
    if user_in.nome_completo is not None:
        user.nome_completo = user_in.nome_completo
    
    if user_in.plano is not None:
        user.plano = user_in.plano
    
    if user_in.verificado is not None:
        user.verificado = user_in.verificado
    
    if user_in.role is not None:
        user.role = user_in.role
    
    user.updated_at = datetime.utcnow()
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/credits", response_model=User)
async def update_user_credits(
    credit_update: CreditUpdate,
    db: Session = Depends(get_db),
    admin: UserModel = Depends(get_admin_user),
) -> Any:
    """
    Add or remove credits from a user - admin only.
    """
    user = db.query(UserModel).filter(UserModel.id == credit_update.userId).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update credits
    user.creditos_disponiveis += credit_update.amount
    
    # Ensure credits don't go below zero
    if user.creditos_disponiveis < 0:
        user.creditos_disponiveis = 0
    
    # Create payment record for tracking
    payment = Payment(
        user_id=user.id,
        amount=credit_update.amount,
        status="completed",
        payment_method="admin",
        description=f"Admin adjustment: {credit_update.reason}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(user)
    db.add(payment)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(
    db: Session = Depends(get_db),
    admin: UserModel = Depends(get_admin_user),
    days: Optional[int] = 30
) -> Any:
    """
    Get system statistics - admin only.
    """
    try:
        # Calculate date for filtering recent data
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # User stats
        total_users = db.query(func.count(UserModel.id)).scalar() or 0
        active_users = db.query(func.count(UserModel.id)).filter(
            UserModel.updated_at >= cutoff_date
        ).scalar() or 0
        
        # Plan distribution
        plan_distribution = {}
        try:
            plans = db.query(
                UserModel.plano, 
                func.count(UserModel.id).label('count')
            ).group_by(UserModel.plano).all()
            
            for plan in plans:
                plan_distribution[plan[0] or 'unknown'] = plan[1]
        except Exception as e:
            print(f"Error getting plan distribution: {str(e)}")
            plan_distribution = {"free": 0, "basic": 0, "pro": 0, "enterprise": 0}
        
        # Chat stats
        total_chats = db.query(func.count(ChatSession.id)).scalar() or 0
        recent_chats = db.query(func.count(ChatSession.id)).filter(
            ChatSession.created_at >= cutoff_date
        ).scalar() or 0
        
        # Document stats
        total_documents = db.query(func.count(Document.id)).scalar() or 0
        recent_documents = db.query(func.count(Document.id)).filter(
            Document.created_at >= cutoff_date
        ).scalar() or 0
        
        # Token usage
        total_token_usage = db.query(func.sum(ChatMessage.tokens)).filter(
            ChatMessage.role == "assistant"
        ).scalar() or 0
        
        recent_token_usage = db.query(func.sum(ChatMessage.tokens)).filter(
            ChatMessage.role == "assistant",
            ChatMessage.created_at >= cutoff_date
        ).scalar() or 0
        
        # Get recent data for charts
        # Daily user signups for the past 30 days
        daily_signups = []
        for day in range(days):
            date = datetime.utcnow() - timedelta(days=day)
            start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
            
            count = db.query(func.count(UserModel.id)).filter(
                UserModel.created_at >= start_of_day,
                UserModel.created_at <= end_of_day
            ).scalar() or 0
            
            daily_signups.append({
                "date": start_of_day.strftime("%Y-%m-%d"),
                "count": count
            })
        
        # Format as a simple daily count array in descending order
        daily_signups = daily_signups[::-1]  # Reverse to get chronological order
        
        # Get token usage over time (for charts)
        daily_token_usage = []
        for day in range(days):
            date = datetime.utcnow() - timedelta(days=day)
            start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
            
            tokens = db.query(func.sum(ChatMessage.tokens)).filter(
                ChatMessage.created_at >= start_of_day,
                ChatMessage.created_at <= end_of_day,
                ChatMessage.role == "assistant"
            ).scalar() or 0
            
            daily_token_usage.append({
                "date": start_of_day.strftime("%Y-%m-%d"),
                "tokens": tokens
            })
        
        # Format as a daily token usage array in descending order
        daily_token_usage = daily_token_usage[::-1]  # Reverse to get chronological order
        
        # Recent activities (combine most recent actions across entities)
        recent_activities = []
        
        try:
            # Recent users
            recent_users = db.query(UserModel).order_by(desc(UserModel.created_at)).limit(5).all()
            for user in recent_users:
                recent_activities.append({
                    "id": user.id,
                    "type": "user_signup",
                    "timestamp": user.created_at.isoformat(),
                    "details": {
                        "user_id": user.id,
                        "email": user.email,
                        "name": user.nome_completo
                    }
                })
        except Exception as e:
            print(f"Error getting recent users: {str(e)}")
        
        try:
            # Recent chats
            recent_chat_sessions = db.query(ChatSession).order_by(desc(ChatSession.created_at)).limit(5).all()
            for session in recent_chat_sessions:
                recent_activities.append({
                    "id": session.id,
                    "type": "chat_session",
                    "timestamp": session.created_at.isoformat(),
                    "details": {
                        "session_id": session.id,
                        "user_id": session.user_id,
                        "title": session.title or "Sem título"
                    }
                })
        except Exception as e:
            print(f"Error getting recent chats: {str(e)}")
        
        try:
            # Recent documents
            recent_docs = db.query(Document).order_by(desc(Document.created_at)).limit(5).all()
            for doc in recent_docs:
                recent_activities.append({
                    "id": doc.id,
                    "type": "document_created",
                    "timestamp": doc.created_at.isoformat(),
                    "details": {
                        "document_id": doc.id,
                        "user_id": doc.user_id,
                        "title": doc.title or "Sem título"
                    }
                })
        except Exception as e:
            print(f"Error getting recent documents: {str(e)}")
        
        # Sort combined activities by timestamp
        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activities = recent_activities[:10]  # Limit to 10 most recent
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "plan_distribution": plan_distribution
            },
            "chats": {
                "total": total_chats,
                "recent": recent_chats
            },
            "documents": {
                "total": total_documents,
                "recent": recent_documents
            },
            "tokens": {
                "total": total_token_usage,
                "recent": recent_token_usage
            },
            "charts": {
                "daily_signups": daily_signups,
                "daily_token_usage": daily_token_usage
            },
            "recent_activities": recent_activities
        }
    except Exception as e:
        import traceback
        print(f"Error in admin stats: {str(e)}")
        print(traceback.format_exc())
        
        # Return fallback data structure
        return {
            "users": {
                "total": 0,
                "active": 0,
                "plan_distribution": {"free": 0, "basic": 0, "pro": 0, "enterprise": 0}
            },
            "chats": {
                "total": 0,
                "recent": 0
            },
            "documents": {
                "total": 0,
                "recent": 0
            },
            "tokens": {
                "total": 0,
                "recent": 0
            },
            "charts": {
                "daily_signups": [{"date": datetime.utcnow().strftime("%Y-%m-%d"), "count": 0}],
                "daily_token_usage": [{"date": datetime.utcnow().strftime("%Y-%m-%d"), "tokens": 0}]
            },
            "recent_activities": [],
            "error": str(e)
        } 

# --- Notification Management Endpoints ---

@router.get("/notifications", response_model=List[NotificationRead])
async def get_all_notifications(
    db: Session = Depends(get_db),
    admin: UserModel = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all notifications - admin only.
    """
    logger.info(f"Admin user {admin.email} fetching notifications (skip={skip}, limit={limit})")
    try:
        notifications_from_db = crud_notification.get_notifications(db, skip=skip, limit=limit)
        logger.info(f"Found {len(notifications_from_db)} notifications in DB.")
        # Logar detalhes básicos de cada notificação encontrada
        # for i, n in enumerate(notifications_from_db):
        #     logger.debug(f"Notification {i}: ID={n.id}, Title={n.title}, CreatedAt={n.created_at}")
            
        # Tentar retornar os dados crus para Pydantic validar
        return notifications_from_db
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}", exc_info=True)
        # print(f"Error getting notifications: {str(e)}") # Usar logger em vez de print
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar notificações: {str(e)}"
        )

@router.post("/notifications", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
async def create_notification(
    *, 
    db: Session = Depends(get_db),
    notification_in: NotificationCreate,
    admin: UserModel = Depends(get_admin_user),
) -> Any:
    """
    Create a new notification - admin only.
    """
    try:
        notification = crud_notification.create_notification(db=db, obj_in=notification_in)
        return notification
    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar notificação: {str(e)}"
        )

@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    *, 
    db: Session = Depends(get_db),
    notification_id: UUID,
    admin: UserModel = Depends(get_admin_user),
) -> None:
    """
    Delete a notification by ID - admin only.
    """
    try:
        deleted_notification = crud_notification.delete_notification(db=db, notification_id=notification_id)
        if not deleted_notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        # Retorna 204 No Content se sucesso
        return None # FastAPI converte None para 204 em rotas DELETE
    except HTTPException as http_exc: # Re-raise HTTP exceptions
        raise http_exc
    except Exception as e:
        print(f"Error deleting notification {notification_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar notificação: {str(e)}"
        ) 