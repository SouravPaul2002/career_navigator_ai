from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Dict
from datetime import datetime

from database import get_session
from auth import get_current_user
from models import User, InterviewSession, InterviewMessage
from interview_agent import generate_interview_response
from pydantic import BaseModel

router = APIRouter()

class SessionStartRequest(BaseModel):
    job_role: str

class ChatRequest(BaseModel):
    message: str

class MessageRead(BaseModel):
    id: int
    sender: str
    content: str
    timestamp: datetime

class SessionRead(BaseModel):
    id: int
    job_role: str
    created_at: datetime
    is_active: bool

@router.post("/sessions", response_model=SessionRead)
async def start_session(
    request: SessionStartRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Start a new interview session."""
    # Deactivate any previous active sessions for this user (optional, but keeps things clean)
    # existing_sessions = session.exec(select(InterviewSession).where(InterviewSession.user_id == current_user.id, InterviewSession.is_active == True)).all()
    # for s in existing_sessions:
    #     s.is_active = False
    #     session.add(s)
    
    new_session = InterviewSession(user_id=current_user.id, job_role=request.job_role)
    session.add(new_session)
    session.commit()
    session.refresh(new_session)
    
    # Generate initial greeting
    greeting_text = f"Hello! I see you're applying for the {request.job_role} position. Let's start with a brief introduction about yourself."
    
    # Save greeting
    initial_message = InterviewMessage(
        session_id=new_session.id,
        sender="ai",
        content=greeting_text
    )
    session.add(initial_message)
    session.commit()
    
    return new_session

@router.get("/sessions", response_model=List[SessionRead])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all interview sessions for the current user."""
    statement = select(InterviewSession).where(InterviewSession.user_id == current_user.id).order_by(InterviewSession.created_at.desc())
    results = session.exec(statement).all()
    return results

@router.get("/sessions/{session_id}/messages", response_model=List[MessageRead])
async def get_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get chat history for a specific session."""
    # Verify session belongs to user
    interview_session = session.get(InterviewSession, session_id)
    if not interview_session or interview_session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
        
    statement = select(InterviewMessage).where(InterviewMessage.session_id == session_id).order_by(InterviewMessage.timestamp.asc())
    results = session.exec(statement).all()
    return results

@router.post("/sessions/{session_id}/chat", response_model=MessageRead)
async def chat(
    session_id: int,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Send a message to the interviewer and get a response."""
    # Verify session
    interview_session = session.get(InterviewSession, session_id)
    if not interview_session or interview_session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not interview_session.is_active:
         raise HTTPException(status_code=400, detail="This interview session has ended.")

    # 1. Save User Message
    user_msg = InterviewMessage(
        session_id=session_id,
        sender="user",
        content=chat_request.message
    )
    session.add(user_msg)
    session.commit() # Commit so we have it in DB (and id is generated)
    
    # 2. Fetch full history for context
    statement = select(InterviewMessage).where(InterviewMessage.session_id == session_id).order_by(InterviewMessage.timestamp.asc())
    history_objs = session.exec(statement).all()
    
    history_dicts = [{"sender": msg.sender, "content": msg.content} for msg in history_objs]
    
    # 3. Generate AI Response
    ai_response_text = generate_interview_response(interview_session.job_role, history_dicts)
    
    # 4. Save AI Response
    ai_msg = InterviewMessage(
        session_id=session_id,
        sender="ai",
        content=ai_response_text
    )
    session.add(ai_msg)
    session.commit()
    session.refresh(ai_msg)
    
    return ai_msg
