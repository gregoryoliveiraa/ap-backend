import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship
from app.db.custom_types import UUIDType
from uuid import uuid4 

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)  # Corrigido de 'message'
    type = Column(String(50), nullable=True)
    is_global = Column(Boolean, default=False)  # Corrigido de 'target_all'
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Corrigido de 'expiry_date'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)  # Campo adicional encontrado no banco
    extra_data = Column('metadata', JSON, nullable=True)  # Mapeia 'metadata' na DB para 'extra_data' no código
    
    # Campos que mantemos na aplicação para compatibilidade com o código existente
    @property
    def message(self):
        return self.content
        
    @property
    def target_all(self):
        return self.is_global
        
    @property
    def expiry_date(self):
        return self.expires_at
    
    # Definir target_users e scheduled_at como propriedades que usam extra_data
    @property
    def target_users(self):
        if self.extra_data and 'target_users' in self.extra_data:
            return self.extra_data.get('target_users')
        return None
        
    @target_users.setter
    def target_users(self, value):
        if not self.extra_data:
            self.extra_data = {}
        self.extra_data['target_users'] = value
    
    @property
    def target_role(self):
        if self.extra_data and 'target_role' in self.extra_data:
            return self.extra_data.get('target_role')
        return None
        
    @target_role.setter
    def target_role(self, value):
        if not self.extra_data:
            self.extra_data = {}
        self.extra_data['target_role'] = value
    
    @property
    def scheduled_at(self):
        if self.extra_data and 'scheduled_at' in self.extra_data:
            return self.extra_data.get('scheduled_at')
        return None
        
    @scheduled_at.setter
    def scheduled_at(self, value):
        if not self.extra_data:
            self.extra_data = {}
        self.extra_data['scheduled_at'] = value
        
    @property
    def action_link(self):
        if self.extra_data and 'action_link' in self.extra_data:
            return self.extra_data.get('action_link')
        return None
        
    @action_link.setter
    def action_link(self, value):
        if not self.extra_data:
            self.extra_data = {}
        self.extra_data['action_link'] = value


# --- Modelo UserNotification ---
class UserNotification(Base):
    __tablename__ = "user_notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4())) 
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True) 
    notification_id = Column(UUIDType(), ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    is_read = Column(Boolean, default=False)  # Nome correto da coluna no banco de dados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Adicionado conforme o banco
    
    # Relationships
    user = relationship("User") # Adicionar back_populates em User se necessário
    notification = relationship("Notification") # Adicionar back_populates em Notification se necessário
# --- Fim UserNotification --- 