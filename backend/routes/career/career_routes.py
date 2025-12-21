import shutil
import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session, select
from resume_analyzer import invoke_agent
from database import get_session
from auth import get_current_user
from models import User, ResumeAnalysis

router = APIRouter()

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Endpoint to analyze a resume and return career insights."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Read file content to check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024 * 1024)}MB"
        )
    
    # Save the uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Invoke the agent with the file path
        res = invoke_agent(temp_file_path)
        
        # Save analysis to database
        db_analysis = ResumeAnalysis(
            user_id=current_user.id,
            filename=file.filename,
            analysis_data=res
        )
        session.add(db_analysis)
        session.commit()
        session.refresh(db_analysis)
        
        return {"message": "Resume analyzed successfully", "data": res, "id": db_analysis.id}
    
    # except Exception as e:
    #     session.rollback()
    #     raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        session.rollback()
        print("Resume analysis error:", e)
        raise HTTPException(
        status_code=500,
        detail="Resume analysis failed. Please try again."
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.get("/history", response_model=List[dict])
async def get_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Fetch history of resume analyses for the current user."""
    statement = select(ResumeAnalysis).where(ResumeAnalysis.user_id == current_user.id).order_by(ResumeAnalysis.created_at.desc())
    results = session.exec(statement).all()
    
    # We'll return a simplified list for history (just metadata + maybe score)
    history = []
    for item in results:
        history.append({
            "id": item.id,
            "filename": item.filename,
            "created_at": item.created_at,
            "score": item.analysis_data.get("analysis", {}).get("score", 0),
            "domain": item.analysis_data.get("analysis", {}).get("identified_domain", "N/A")
        })
    return history

@router.get("/analysis/{analysis_id}")
async def get_analysis_detail(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Fetch details of a specific past analysis."""
    statement = select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id, ResumeAnalysis.user_id == current_user.id)
    analysis = session.exec(statement).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis.analysis_data