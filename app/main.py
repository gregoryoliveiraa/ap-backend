# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.api.routes import auth, ai, documents

# Cria a aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API da Advogada Parceira: Assistente de IA para textos jurídicos",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS] + [settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os roteadores
app.include_router(auth.router, prefix="/api/auth", tags=["autenticação"])
app.include_router(ai.router, prefix="/api/ai", tags=["inteligência artificial"])
app.include_router(documents.router, prefix="/api/documents", tags=["documentos"])

# Rota de teste para verificar se a API está funcionando
@app.get("/api/healthcheck")
async def healthcheck():
    return JSONResponse(
        status_code=200,
        content={
            "status": "online",
            "project": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT
        }
    )

# Rota raiz
@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API da Advogada Parceira. Acesse /api/docs para documentação."
    }

# Para execução direta com python main.py
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )