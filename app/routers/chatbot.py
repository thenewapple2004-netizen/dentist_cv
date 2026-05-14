from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from app.models.user import User
from app.routers.deps import get_current_user
from app.services.chatbot_service import chat_with_ai

router = APIRouter(prefix="/api/chat", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []


from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analysis import ChatMessage

@router.post("/message")
async def send_message(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Save user message
    db.add(ChatMessage(user_id=current_user.id, role="user", content=req.message))
    
    response = await chat_with_ai(req.message, req.history, current_user.role)
    
    # Save assistant response
    db.add(ChatMessage(user_id=current_user.id, role="assistant", content=response))
    db.commit()
    
    return {"response": response, "role": "assistant"}
