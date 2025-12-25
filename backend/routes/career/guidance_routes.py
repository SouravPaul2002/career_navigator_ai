from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional

from database import get_session
from auth import get_current_user
from models import User, UserRoadmap, UserRoadmapStep
from guidance_agent import generate_roadmap, get_topic_details, generate_quiz
from ai_schema.schema import CareerRoadmap

router = APIRouter()

class RoadmapRequest(BaseModel):
    job_role: str

class TopicRequest(BaseModel):
    topic: str
    role: str = "General"

class QuizRequest(BaseModel):
    topic: str

class StepStatusUpdate(BaseModel):
    status: str # todo, in_progress, done

class UserRoadmapRead(BaseModel):
    id: int
    role: str
    steps: List[dict]

@router.post("/generate", response_model=CareerRoadmap)
async def generate_career_roadmap_endpoint(
    request: RoadmapRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not request.job_role.strip():
        raise HTTPException(status_code=400, detail="Job role cannot be empty.")
    roadmap = generate_roadmap(request.job_role)
    if not roadmap:
        raise HTTPException(status_code=500, detail="Failed to generate roadmap.")
    return roadmap

@router.post("/save")
async def save_roadmap(
    roadmap_data: CareerRoadmap,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Save a generated roadmap as the active roadmap for the user."""
    # Deactivate existing roadmaps
    existing = session.exec(select(UserRoadmap).where(UserRoadmap.user_id == current_user.id, UserRoadmap.is_active == True)).all()
    for rm in existing:
        rm.is_active = False
        session.add(rm)
    
    # Create new roadmap
    new_roadmap = UserRoadmap(user_id=current_user.id, role=roadmap_data.role)
    session.add(new_roadmap)
    session.commit()
    session.refresh(new_roadmap)
    
    # Create steps
    for idx, step in enumerate(roadmap_data.steps):
        db_step = UserRoadmapStep(
            roadmap_id=new_roadmap.id,
            title=step.step_title,
            description=step.description,
            estimated_duration=step.estimated_duration,
            status="todo",
            order_index=idx
        )
        session.add(db_step)
    
    session.commit()
    return {"message": "Roadmap saved successfully", "id": new_roadmap.id}

@router.get("/active")
async def get_active_roadmap(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get the user's currently active roadmap."""
    roadmap = session.exec(select(UserRoadmap).where(UserRoadmap.user_id == current_user.id, UserRoadmap.is_active == True)).first()
    if not roadmap:
        return None
    
    steps = session.exec(select(UserRoadmapStep).where(UserRoadmapStep.roadmap_id == roadmap.id).order_by(UserRoadmapStep.order_index)).all()
    
    return {
        "id": roadmap.id,
        "role": roadmap.role,
        "steps": [step.model_dump() for step in steps]
    }

@router.patch("/steps/{step_id}")
async def update_step_status(
    step_id: int,
    update: StepStatusUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update the status of a specific step."""
    step = session.get(UserRoadmapStep, step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
        
    # Verify ownership via roadmap
    roadmap = session.get(UserRoadmap, step.roadmap_id)
    if roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    step.status = update.status
    session.add(step)
    session.commit()
    return {"message": "Status updated"}

@router.post("/details")
async def get_details(
    request: TopicRequest,
    current_user: User = Depends(get_current_user)
):
    """Get detailed explanation for a topic."""
    details = get_topic_details(request.topic, request.role)
    return {"content": details}

@router.post("/quiz")
async def get_quiz(
    request: QuizRequest,
    current_user: User = Depends(get_current_user)
):
    """Get a quiz for a topic."""
    questions = generate_quiz(request.topic)
    return questions
