from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.auth.jwt import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/profile", response_model=UserRead)
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.name is not None:
        current_user.name = data.name
    if data.branch is not None:
        current_user.branch = data.branch
    if data.year is not None:
        current_user.year = data.year
    if data.bio is not None:
        current_user.bio = data.bio
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

