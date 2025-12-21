from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import get_session
from models import User, UserCreate, UserRead, Token, UserUpdate, PasswordChange
from auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/signup", response_model=UserRead)
def signup(user: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, name=user.name, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserRead)
def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.email is not None:
        # Check if email is already taken
        statement = select(User).where(User.email == user_update.email)
        existing_user = session.exec(statement).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already taken")
        current_user.email = user_update.email
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@router.post("/me/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password changed successfully"}

@router.delete("/me")
def delete_user_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    session.delete(current_user)
    session.commit()
    return {"message": "User deleted successfully"}