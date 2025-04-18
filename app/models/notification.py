import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship
# Importar uuid4 para o default do id de UserNotification
from uuid import uuid4 

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, default='info') # info, warning, success, error
    target_all = Column(Boolean, default=False)
    target_role = Column(String(50), nullable=True, index=True) # 'admin', 'user', etc.
    target_users = Column(JSON, nullable=True) # Lista de IDs de usuários específicos
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    action_link = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Adicione aqui relacionamentos se necessário, por exemplo, com quem criou a notificação
    # creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    # creator = relationship("User")
    # Relationship para UserNotification (se for mantido)
    # user_entries = relationship("UserNotification", back_populates="notification", cascade="all, delete-orphan")


# --- Modelo UserNotification Reativado e Corrigido ---
class UserNotification(Base):
    __tablename__ = "user_notifications"
    
    # Usar UUID para o ID da própria tabela, por consistência?
    # Ou manter String como está? Vou manter String por enquanto.
    id = Column(String, primary_key=True, default=lambda: str(uuid4())) 
    # user_id deve ser String para corresponder a User.id
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True) 
    # notification_id deve ser UUID para corresponder a Notification.id
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True) 
    read = Column(Boolean, default=False)
    delivered = Column(Boolean, default=True) # Assumir entregue ao ser criado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User") # Adicionar back_populates em User se necessário
    notification = relationship("Notification") # Adicionar back_populates em Notification se necessário
# --- Fim UserNotification --- 