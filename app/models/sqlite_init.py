# app/models/sqlite_init.py
from sqlalchemy.orm import relationship

def init_relationships():
    """
    Inicializa relacionamentos entre os modelos SQLite.
    Função para ser chamada após a criação das tabelas.
    """
    print("Inicializando relacionamentos SQLite...")
    
    try:
        # Importa todos os modelos SQLite
        from app.models.user_sqlite import User
        from app.models.document_sqlite import Document
        from app.models.chat_sqlite import ChatHistory

        # Define relacionamentos bidirecionais entre os modelos
        # Isso evita importações circulares ao definir os relacionamentos aqui

        # Relacionamentos do User
        User.documents = relationship("Document", back_populates="user", 
                                    foreign_keys=[Document.created_by],
                                    cascade="all, delete-orphan")

        User.chat_histories = relationship("ChatHistory", back_populates="user", 
                                        foreign_keys=[ChatHistory.user_id],
                                        cascade="all, delete-orphan")

        # Relacionamentos do Document
        Document.user = relationship("User", back_populates="documents", 
                                foreign_keys=[Document.created_by])

        # Relacionamentos do ChatHistory
        ChatHistory.user = relationship("User", back_populates="chat_histories", 
                                    foreign_keys=[ChatHistory.user_id])
        
        print("Relacionamentos inicializados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao inicializar relacionamentos: {e}")
        import traceback
        traceback.print_exc()