from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.router import api_router
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.user import User
from app.core.security import create_access_token, verify_password
from datetime import timedelta, datetime
from app.db.base import init_db
import logging

# Configure logging
logger = logging.getLogger(__name__)

# API version
API_VERSION = "2.1.8"

app = FastAPI(
    title=settings.API_TITLE,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    version=API_VERSION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    expose_headers=["Content-Length", "Content-Range"],
    max_age=3600,
)

# Initialize database
init_db()

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    response = await call_next(request)
    duration = datetime.now() - start_time
    
    # Log request details
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {duration.total_seconds():.3f}s "
        f"Origin: {request.headers.get('origin', 'Unknown')}"
    )
    
    # Log CORS issues
    if response.status_code == 403 and request.headers.get("origin"):
        logger.warning(
            f"Possible CORS issue - Origin: {request.headers.get('origin')} "
            f"Method: {request.method}"
        )
    
    return response

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {"message": "Advogada Parceira API is running", "status": "ok", "version": API_VERSION}


@app.get("/test_login")
async def test_login(db: Session = Depends(get_db)):
    """
    Test login endpoint for debugging
    """
    try:
        admin_email = "admin@example.com"
        admin_password = "admin123"
        
        # Find user in DB
        user = db.query(User).filter(User.email == admin_email).first()
        
        if not user:
            return {"status": "error", "message": "User not found"}
            
        # Verify password
        is_password_valid = verify_password(admin_password, user.hashed_password)
        
        if not is_password_valid:
            return {"status": "error", "message": "Invalid password"}
        
        # Generate token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            user.id, expires_delta=access_token_expires
        )
        
        return {
            "status": "success",
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "nome_completo": user.nome_completo
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {"status": "error", "message": str(e), "details": error_details}


@app.get("/test_login_sidarta")
async def test_login_sidarta(db: Session = Depends(get_db)):
    """
    Test login endpoint for Sidarta user - for debugging
    """
    try:
        # Dados de teste
        email = "sidarta.martins@gmail.com"
        password = "123456"
        
        # Find user in DB
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Print hash details for debugging
        logger.info(f"User ID: {user.id}")
        logger.info(f"User email: {user.email}")
        logger.info(f"Hashed password: {user.hashed_password}")
        logger.info(f"Hash length: {len(user.hashed_password)}")
        
        # Verify password
        try:
            is_password_valid = verify_password(password, user.hashed_password)
            logger.info(f"Password verification result: {is_password_valid}")
        except Exception as verify_error:
            logger.error(f"Password verification error: {str(verify_error)}")
            return {"status": "error", "message": f"Password verification error: {str(verify_error)}"}
        
        if not is_password_valid:
            return {"status": "error", "message": "Invalid password"}
        
        # Generate token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        try:
            access_token = create_access_token(
                user.id, expires_delta=access_token_expires
            )
            logger.info("Access token created successfully")
        except Exception as token_error:
            logger.error(f"Token creation error: {str(token_error)}")
            return {"status": "error", "message": f"Token creation error: {str(token_error)}"}
        
        return {
            "status": "success",
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "nome_completo": user.nome_completo
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {"status": "error", "message": str(e), "details": error_details}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
