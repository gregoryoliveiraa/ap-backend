from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional
from uuid import UUID

from app.models.notification import Notification, UserNotification
from app.models.user import User # Importar User para buscar por role/id
from app.schemas.notification import NotificationCreate

def get_notifications(db: Session, skip: int = 0, limit: int = 100) -> List[Notification]:
    """
    Recupera todas as notificações do banco de dados, ordenadas pela data de criação.
    """
    return db.query(Notification).order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

def create_notification(db: Session, *, obj_in: NotificationCreate) -> Notification:
    """
    Cria uma nova notificação e as entradas UserNotification correspondentes.
    """
    # 1. Criar a notificação principal
    try:
      notification_data = obj_in.model_dump(exclude_unset=True) 
    except AttributeError:
       notification_data = obj_in.dict(exclude_unset=True)
        
    db_notification = Notification(**notification_data)
    db.add(db_notification)
    # Commit inicial para obter o ID da notificação
    # Um commit aqui pode ser problemático se a criação de UserNotification falhar
    # Idealmente, faríamos tudo em uma transação, mas por simplicidade:
    try:
        db.commit()
        db.refresh(db_notification)
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar notificação principal: {e}")
        raise

    # 2. Determinar usuários alvo e criar UserNotification
    target_user_ids = set()
    
    if db_notification.target_all:
        users = db.query(User.id).filter(User.is_active == True).all()
        target_user_ids.update([user.id for user in users])
    elif db_notification.target_role:
        users = db.query(User.id).filter(
            User.is_active == True,
            User.role == db_notification.target_role
        ).all()
        target_user_ids.update([user.id for user in users])
    elif db_notification.target_users:
        # Garantir que os IDs sejam strings (como User.id)
        target_user_ids.update([str(user_id) for user_id in db_notification.target_users])

    # 3. Criar entradas UserNotification em lote (mais eficiente)
    user_notifications_to_create = []
    for user_id in target_user_ids:
        user_notifications_to_create.append(
            UserNotification(
                user_id=user_id,
                notification_id=db_notification.id
                # read e delivered têm defaults no modelo
            )
        )
    
    if user_notifications_to_create:
        try:
            db.bulk_save_objects(user_notifications_to_create)
            db.commit() 
            print(f"Criadas {len(user_notifications_to_create)} entradas UserNotification para notificação {db_notification.id}")
        except Exception as e:
            db.rollback() # Tenta reverter a criação das UserNotifications
            # Idealmente, deletaríamos a Notification principal aqui também se a entrega falhar
            print(f"Erro ao criar entradas UserNotification: {e}")
            # Propagar o erro ou lidar de forma mais robusta (ex: marcar notificação como falha)
            # Por enquanto, vamos apenas logar e retornar a notificação criada

    return db_notification # Retorna a notificação principal criada

def get_notification(db: Session, notification_id: UUID) -> Optional[Notification]:
    """
    Recupera uma notificação específica pelo ID.
    """
    return db.query(Notification).filter(Notification.id == notification_id).first()

def delete_notification(db: Session, *, notification_id: UUID) -> Optional[Notification]:
    """
    Deleta uma notificação e suas entradas UserNotification associadas.
    """
    # Deletar entradas UserNotification primeiro (devido à FK)
    db.query(UserNotification).filter(UserNotification.notification_id == notification_id).delete(synchronize_session=False)
    
    # Deletar a notificação principal
    db_obj = db.query(Notification).filter(Notification.id == notification_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
        print(f"Notificação {notification_id} e suas entradas UserNotification deletadas.")
        return db_obj
    else:
        db.rollback() # Reverter delete de UserNotification se a Notification não for encontrada
        print(f"Notificação {notification_id} não encontrada para deleção.")
        return None 