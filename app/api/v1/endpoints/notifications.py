from typing import Any, List, Dict, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_
from uuid import UUID
import logging
import json

from app.api.dependencies import get_db, get_admin_user, get_current_user
from app.models.user import User as UserModel
from app.models.notification import Notification as NotificationModel, UserNotification
from app.schemas.notification import NotificationRead

router = APIRouter()

logger = logging.getLogger(__name__)

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
    now = datetime.utcnow()

    try:
        # Buscar entradas UserNotification para o usuário atual
        user_notif_entries = db.query(UserNotification).filter(
            UserNotification.user_id == current_user.id
        ).all()
        logger.info(f"Found {len(user_notif_entries)} UserNotification entries for user {current_user.id}")
        
        if not user_notif_entries:
            logger.info(f"No notification entries found for user {current_user.id}, returning empty list.")
            return []
            
        user_notif_map = {un.notification_id: un for un in user_notif_entries}
        notification_ids = list(user_notif_map.keys())
        
        if not notification_ids:
            logger.info(f"No notification IDs found for user {current_user.id}, returning empty list.")
            return []

        logger.info(f"Fetching Notification details for IDs: {notification_ids}")
        notifications = db.query(NotificationModel).filter(
            NotificationModel.id.in_(notification_ids),
            or_(
                NotificationModel.expiry_date == None, 
                NotificationModel.expiry_date > now
            ),
            or_(
                NotificationModel.scheduled_at == None,
                NotificationModel.scheduled_at <= now
            )
        ).order_by(desc(NotificationModel.created_at)).all()
        logger.info(f"Found {len(notifications)} active and scheduled Notification details.")
        
        if not notifications:
            logger.info(f"No active notifications found for user {current_user.id}, returning empty list.")
            return []
            
        notifications_with_read_status = []
        for notification in notifications:
            try:
                user_entry = user_notif_map.get(notification.id)
                read_status = user_entry.is_read if user_entry else False  # Usar is_read em vez de read
                
                # Certificar que target_users seja sempre uma lista de strings válida
                target_users_processed = []
                
                # Se target_users existir no objeto notification, processá-lo
                if hasattr(notification, 'target_users') and notification.target_users is not None:
                    # Se for string (JSON serializado), tentar deserializar
                    if isinstance(notification.target_users, str):
                        try:
                            target_users_processed = json.loads(notification.target_users)
                            # Garantir que agora é uma lista
                            if not isinstance(target_users_processed, list):
                                target_users_processed = []
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Failed to parse target_users as JSON for notification {notification.id}")
                            target_users_processed = []
                    # Se já for um dict/list (depende do driver SQLAlchemy), usar diretamente
                    elif isinstance(notification.target_users, (list, dict)):
                        target_users_processed = notification.target_users
                        if isinstance(target_users_processed, dict):
                            # Converter dict para lista se for o caso
                            target_users_processed = list(target_users_processed.values())
                
                # Garantir que todos os itens sejam strings
                target_users_str = []
                for item in target_users_processed:
                    if item is not None:
                        target_users_str.append(str(item))
                
                # Atualizar o objeto notification com a lista processada
                notification.target_users = target_users_str
                
                # Adicionar o status de leitura
                setattr(notification, 'read', read_status)  # Mantenha o nome 'read' para a resposta API
                logger.debug(f"Notification ID: {notification.id}, Title: {notification.title}, Read: {read_status}, target_users: {notification.target_users}")
                
                notifications_with_read_status.append(notification)
            except Exception as e:
                logger.error(f"Error processing notification {notification.id}: {str(e)}", exc_info=True)
                continue
        
        # Retornar lista vazia se nenhuma notificação foi processada com sucesso
        if not notifications_with_read_status:
            logger.warning("No notifications could be processed successfully")
            return []
            
        return notifications_with_read_status
    except Exception as e:
        logger.error(f"Error fetching user notifications for user {current_user.id}: {e}", exc_info=True)
        return []  # Retorna uma lista vazia em vez de um erro 500

@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Mark a notification as read for the current user.
    """
    try:
        user_notification = db.query(UserNotification).filter(
            UserNotification.notification_id == notification_id,
            UserNotification.user_id == current_user.id
        ).first()
        
        if not user_notification:
            logger.warning(f"UserNotification entry not found for notification_id={notification_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found for this user"
            )
        
        # Atualizar o status de leitura
        user_notification.is_read = True  # Usar is_read em vez de read
        db.commit()
        
        return {"success": True, "message": "Notification marked as read"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}", exc_info=True)
        return {"success": False, "message": "Failed to mark notification as read"} 