from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User

router = APIRouter()

@router.get("/")
async def search_jurisprudence(
    query: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search jurisprudence
    """
    return {
        "status": "success",
        "message": "Jurisprudence search endpoint is not fully implemented yet",
        "data": [],
        "query": query
    }
