from typing import Any, List, Dict, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_
from uuid import UUID
import logging # Importar logging

from app.api.dependencies import get_db, get_admin_user, get_current_user
from app.models.user import User as UserModel
from app.models.notification import Notification as NotificationModel, UserNotification
from app.schemas.notification import NotificationRead

router = APIRouter()

logger = logging.getLogger(__name__) # Configurar logger

# --- Rota para usuários buscarem suas notificações ---

@router.get("", response_model=List[NotificationRead])
async def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get current user's relevant notifications (non-expired).
    Inclui o status 'read' para cada notificação.
    """
    logger.info(f"Fetching notifications for user ID: {current_user.id}")
    now = datetime.utcnow() # Usar UTC se as datas no DB são UTC

    try:
        # Buscar entradas UserNotification para o usuário atual
        user_notif_entries = db.query(UserNotification).filter(
            UserNotification.user_id == current_user.id
        ).all()
        logger.info(f"Found {len(user_notif_entries)} UserNotification entries for user {current_user.id}")
        
        user_notif_map = {un.notification_id: un for un in user_notif_entries}
        notification_ids = list(user_notif_map.keys())
        
        if not notification_ids:
            logger.info(f"No notification IDs found for user {current_user.id}, returning empty list.")
            return [] # Retorna lista vazia se não há notificações para este usuário

        logger.info(f"Fetching Notification details for IDs: {notification_ids}")
        # Buscar os detalhes das notificações correspondentes que:
        # 1. Não expiraram
        # 2. Não estão agendadas OU a hora agendada já passou
        notifications = db.query(NotificationModel).filter(
            NotificationModel.id.in_(notification_ids),
            or_(
                NotificationModel.expiry_date == None, 
                NotificationModel.expiry_date > now
            ),
            # Adicionar filtro de agendamento
            or_(
                NotificationModel.scheduled_at == None,
                NotificationModel.scheduled_at <= now
            )
        ).order_by(desc(NotificationModel.created_at)).all()
        logger.info(f"Found {len(notifications)} active and scheduled Notification details.")
        
        # Adicionar o status 'read' e preparar a resposta com o schema correto
        notifications_with_read_status = []
        for notification in notifications:
            user_entry = user_notif_map.get(notification.id)
            read_status = user_entry.read if user_entry else False
            setattr(notification, 'read', read_status) # Adiciona dinamicamente para validação do schema
            logger.debug(f"  Notification ID: {notification.id}, Title: {notification.title}, Read: {read_status}")
            notifications_with_read_status.append(notification)
            
        return notifications_with_read_status
    except Exception as e:
        logger.error(f"Error fetching user notifications for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch notifications")

# --- Rota para marcar como lida ---

@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: UUID, # Agora UUID está definido
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> None:
    """
    Mark a specific notification as read for the current user.
    """
    user_notification = db.query(UserNotification).filter(
        UserNotification.user_id == current_user.id,
        UserNotification.notification_id == notification_id
    ).first()
    
    if not user_notification:
        # Não levantar erro se a notificação/entrada não existir, apenas retornar
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail="User notification entry not found"
        # )
        return None # Retorna 204 mesmo se não encontrado
    
    if not user_notification.read:
        user_notification.read = True
        db.add(user_notification)
        db.commit()
    
    return None # Retorna 204 No Content

# --- Fim das rotas do usuário ---

# --- Rotas comentadas pois dependem de UserNotification ou conflitam com admin.py ---

# @router.get("/admin", response_model=List[Notification])
# async def get_all_notifications(
#     db: Session = Depends(get_db),
#     admin: UserModel = Depends(get_admin_user),
# ) -> Any:
#     """
#     Get all notifications (admin only)
#     """
#     notifications = db.query(NotificationModel).order_by(desc(NotificationModel.created_at)).all()
#     return notifications


# @router.post("", response_model=Notification)
# async def create_notification(
#     notification_in: NotificationCreate,
#     db: Session = Depends(get_db),
#     admin: UserModel = Depends(get_admin_user),
# ) -> Any:
#     """
#     Create a new notification (admin only)
#     """
#     # Create the notification
#     notification = NotificationModel(
#         title=notification_in.title,
#         message=notification_in.message,
#         type=notification_in.type,
#         target_users=notification_in.target_users,
#         target_role=notification_in.target_role,
#         target_all=notification_in.target_all,
#         expiry_date=notification_in.expiry_date,
#         action_link=notification_in.action_link,
#         created_by=admin.id
#     )
    
#     db.add(notification)
#     db.commit()
#     db.refresh(notification)
    
#     # Determine target users
#     target_users = []
    
#     if notification_in.target_all:
#         # Target all users
#         users = db.query(UserModel).filter(UserModel.is_active == True).all()
#         target_users = [user.id for user in users]
#     elif notification_in.target_role:
#         # Target users with a specific role
#         users = db.query(UserModel).filter(
#             UserModel.is_active == True,
#             UserModel.role == notification_in.target_role
#         ).all()
#         target_users = [user.id for user in users]
#     elif notification_in.target_users:
#         # Target specific users
#         target_users = notification_in.target_users
    
#     # Create user notification entries
#     for user_id in target_users:
#         user_notification = UserNotification(
#             user_id=user_id,
#             notification_id=notification.id
#         )
#         db.add(user_notification)
    
#     db.commit()
    
#     return notification


# @router.delete("/{notification_id}", response_model=Dict[str, Any])
# async def delete_notification(
#     notification_id: str,
#     db: Session = Depends(get_db),
#     admin: UserModel = Depends(get_admin_user),
# ) -> Any:
#     """
#     Delete a notification (admin only)
#     """
#     notification = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    
#     if not notification:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Notification not found"
#         )
    
#     # Delete user notification records
#     db.query(UserNotification).filter(UserNotification.notification_id == notification_id).delete()
    
#     # Delete the notification
#     db.delete(notification)
#     db.commit()
    
#     return {"message": "Notification deleted successfully"}

# --- Fim das rotas comentadas --- 