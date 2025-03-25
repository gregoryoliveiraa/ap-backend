# app/models/__init__.py
# Este arquivo apenas importa os modelos para garantir que sejam registrados
try:
    from app.models.user import User
    from app.models.document import Document
    from app.models.chat import ChatHistory
except ImportError as e:
    print(f"Erro ao importar modelos: {e}")