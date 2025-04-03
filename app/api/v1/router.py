from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, documents, chat, jurisprudence, usage

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(jurisprudence.router, prefix="/jurisprudence", tags=["jurisprudence"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
