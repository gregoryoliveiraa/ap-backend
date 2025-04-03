from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
import json
import asyncio

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.chat_session import ChatSession as ChatSessionModel
from app.models.chat_message import ChatMessage as ChatMessageModel
from app.models.usage import Usage
from app.api.v1.schemas.chat import ChatSession, ChatMessageCreate, ChatMessage, ChatRequest, ChatResponse, ChatSessionCreate, ChatSessionUpdate
from app.core.ai_providers import AIProviderManager, AIProvider
from datetime import datetime
from app.api.v1.endpoints.usage import calcular_creditos_consumidos

router = APIRouter()
ai_manager = AIProviderManager()

PROVIDER_MAP = {
    "openai": AIProvider.OPENAI,
    "claude": AIProvider.CLAUDE,
    "deepseek": AIProvider.DEEPSEEK
}

@router.get("/", response_model=List[ChatSession])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve chat sessions for the current user
    """
    query = db.query(ChatSessionModel).options(
        joinedload(ChatSessionModel.messages)
    ).filter(ChatSessionModel.user_id == current_user.id)
    
    sessions = query.order_by(ChatSessionModel.updated_at.desc()).offset(skip).limit(limit).all()
    
    # Sort messages by created_at for each session
    for session in sessions:
        if session.messages:
            session.messages.sort(key=lambda x: x.created_at)
    
    return sessions

@router.post("/", response_model=ChatSession)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new chat session
    """
    db_session = ChatSessionModel(
        user_id=current_user.id,
        title=session_data.title
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # Add system welcome message
    welcome_message = ChatMessageModel(
        session_id=db_session.id,
        content="Olá! Sou a Advogada Parceira, sua assistente jurídica especializada no sistema legal brasileiro. Como posso ajudar você hoje?",
        role="assistant",
        tokens_used=0
    )
    
    db.add(welcome_message)
    db.commit()
    
    return db_session

@router.get("/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific chat session with messages
    """
    db_session = db.query(ChatSessionModel).options(
        joinedload(ChatSessionModel.messages)
    ).filter(
        ChatSessionModel.id == session_id,
        ChatSessionModel.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Sort messages by created_at
    if db_session.messages:
        db_session.messages.sort(key=lambda x: x.created_at)
    
    return db_session

@router.patch("/{session_id}", response_model=ChatSession)
async def update_chat_session(
    session_id: str,
    session_data: ChatSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a chat session (title)
    """
    db_session = db.query(ChatSessionModel).filter(
        ChatSessionModel.id == session_id,
        ChatSessionModel.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    if session_data.title is not None:
        db_session.title = session_data.title
    
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.delete("/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a chat session and all its messages
    """
    db_session = db.query(ChatSessionModel).filter(
        ChatSessionModel.id == session_id,
        ChatSessionModel.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Delete all messages first
    db.query(ChatMessageModel).filter(ChatMessageModel.session_id == session_id).delete()
    
    # Then delete the session
    db.delete(db_session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI and get a response
    """
    # Get the session
    db_session = db.query(ChatSessionModel).filter(
        ChatSessionModel.id == request.session_id,
        ChatSessionModel.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Save the user message
    user_message = ChatMessageModel(
        session_id=db_session.id,
        content=request.message,
        role="user",
        tokens_used=0
    )
    
    db.add(user_message)
    db.commit()
    
    # Check if this is the first user message and update the title
    # Count the messages in the session
    message_count = db.query(ChatMessageModel).filter(
        ChatMessageModel.session_id == db_session.id,
        ChatMessageModel.role == 'user'
    ).count()
    
    # If this is the first user message (message_count would be 1 including the one we just added)
    if message_count == 1:
        # Create a title from the first 30 chars of the message
        title = request.message[:30]
        if len(request.message) > 30:
            title += "..."
        
        # Update the session title
        db_session.title = title
        db.commit()
    
    # Get AI response
    try:
        provider = PROVIDER_MAP.get(request.provider, AIProvider.DEEPSEEK)
        ai_response = ai_manager.get_response(
            user_message=request.message,
            session_id=db_session.id,
            provider=provider
        )
        
        # Save the AI response
        assistant_message = ChatMessageModel(
            session_id=db_session.id,
            content=ai_response.message,
            role="assistant",
            tokens_used=ai_response.tokens_used,
            provider=request.provider
        )
        
        db.add(assistant_message)
        db.commit()
        
        # Update session timestamp
        db_session.updated_at = datetime.utcnow()
        
        # Update user's credits
        if ai_response.tokens_used > 0 and current_user.creditos_disponiveis is not None:
            # Calcular créditos a serem consumidos usando a função comum
            creditos_a_consumir = calcular_creditos_consumidos(ai_response.tokens_used)
            current_user.creditos_disponiveis = max(0, current_user.creditos_disponiveis - creditos_a_consumir)
            print(f"Tokens usados: {ai_response.tokens_used}, Créditos consumidos: {creditos_a_consumir}")
            
            # Update usage statistics
            usage = db.query(Usage).filter(Usage.user_id == current_user.id).first()
            if usage:
                usage.total_tokens = usage.total_tokens + ai_response.tokens_used
                usage.updated_at = datetime.utcnow()
            
            db.commit()
        
        db.commit()
        
        return ChatResponse(
            message=ai_response.message,
            session_id=db_session.id,
            tokens_used=ai_response.tokens_used
        )
    except Exception as e:
        # Log the error
        print(f"Error getting AI response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stream chat responses from the AI
    """
    # Get the session
    db_session = db.query(ChatSessionModel).filter(
        ChatSessionModel.id == request.session_id,
        ChatSessionModel.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Save the user message
    user_message = ChatMessageModel(
        session_id=db_session.id,
        content=request.message,
        role="user",
        tokens_used=0
    )
    
    db.add(user_message)
    db.commit()
    
    # Check if this is the first user message and update the title
    # Count the messages in the session
    message_count = db.query(ChatMessageModel).filter(
        ChatMessageModel.session_id == db_session.id,
        ChatMessageModel.role == 'user'
    ).count()
    
    # If this is the first user message (message_count would be 1 including the one we just added)
    if message_count == 1:
        # Create a title from the first 30 chars of the message
        title = request.message[:30]
        if len(request.message) > 30:
            title += "..."
        
        # Update the session title
        db_session.title = title
        db.commit()
    
    # Define the streaming response function
    async def generate():
        try:
            provider = PROVIDER_MAP.get(request.provider, AIProvider.DEEPSEEK)
            
            # Get AI response (non-streaming for now, but we'll simulate streaming)
            ai_response = ai_manager.get_response(
                user_message=request.message,
                session_id=db_session.id,
                provider=provider
            )
            
            # Save the AI response
            assistant_message = ChatMessageModel(
                session_id=db_session.id,
                content=ai_response.message,
                role="assistant",
                tokens_used=ai_response.tokens_used,
                provider=request.provider
            )
            
            db.add(assistant_message)
            db.commit()
            
            # Update session timestamp
            db_session.updated_at = datetime.utcnow()
            
            # Update user's credits
            if ai_response.tokens_used > 0 and current_user.creditos_disponiveis is not None:
                # Calcular créditos a serem consumidos usando a função comum
                creditos_a_consumir = calcular_creditos_consumidos(ai_response.tokens_used)
                current_user.creditos_disponiveis = max(0, current_user.creditos_disponiveis - creditos_a_consumir)
                print(f"Tokens usados: {ai_response.tokens_used}, Créditos consumidos: {creditos_a_consumir}")
                
                # Update usage statistics
                usage = db.query(Usage).filter(Usage.user_id == current_user.id).first()
                if usage:
                    usage.total_tokens = usage.total_tokens + ai_response.tokens_used
                    usage.updated_at = datetime.utcnow()
                
                db.commit()
            
            db.commit()
            
            # Stream the response by words
            words = ai_response.message.split()
            current_chunk = ""
            
            for i, word in enumerate(words):
                current_chunk += word + " "
                
                # Send chunks of 3-5 words
                if i % 4 == 0 and i > 0:
                    # Create SSE format
                    data = {
                        "content": current_chunk,
                        "done": False
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    await asyncio.sleep(0.1)  # Simulate network delay
                    current_chunk = ""
            
            # Send any remaining text
            if current_chunk:
                data = {
                    "content": current_chunk,
                    "done": False
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            # Send completion message
            data = {
                "content": "",
                "done": True,
                "tokens_used": ai_response.tokens_used,
                "provider": request.provider
            }
            yield f"data: {json.dumps(data)}\n\n"
            
        except Exception as e:
            # Log the error
            print(f"Error streaming AI response: {str(e)}")
            data = {
                "error": f"Error processing message: {str(e)}",
                "done": True
            }
            yield f"data: {json.dumps(data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
