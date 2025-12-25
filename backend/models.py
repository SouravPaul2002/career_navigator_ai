from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON, Column
from pydantic import validator
import re
from datetime import datetime

# Shared properties
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None

# Database model
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

# Properties to return via API
class UserRead(UserBase):
    id: int

# Properties to receive via API on update
class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None

class PasswordChange(SQLModel):
    old_password: str
    new_password: str

# Token schemas
class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: Optional[str] = None

# Resume Analysis Models
class ResumeAnalysisBase(SQLModel):
    filename: str
    analysis_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResumeAnalysis(ResumeAnalysisBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

class ResumeAnalysisRead(ResumeAnalysisBase):
    id: int
    user_id: int

# Interview Models
class InterviewSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    job_role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

class InterviewMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="interviewsession.id")
    sender: str  # "user" or "ai"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Career Roadmap Models
class UserRoadmap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

class UserRoadmapStep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    roadmap_id: int = Field(foreign_key="userroadmap.id")
    title: str
    description: str
    estimated_duration: str
    status: str = Field(default="todo") # todo, in_progress, done
    order_index: int
