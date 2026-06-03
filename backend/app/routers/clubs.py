from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.user import User
from app.schemas.club import ClubCreate, ClubRead
from app.services import club_service
from app.auth.jwt import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ClubRead])
def get_clubs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return club_service.get_clubs(db, skip=skip, limit=limit)

@router.get("/{club_id}", response_model=ClubRead)
def get_club(club_id: int, db: Session = Depends(get_db)):
    club = club_service.get_club_by_id(db, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return club

@router.post("/", response_model=ClubRead, status_code=201)
def create_club(club: ClubCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return club_service.create_club(db, club, president_id=current_user.id)

@router.post("/{club_id}/join", status_code=200)
def join_club(club_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = club_service.get_club_by_id(db, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    club_service.join_club(db, club_id, current_user.id)
    return {"detail": "Joined club"}

@router.post("/{club_id}/leave", status_code=200)
def leave_club(club_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = club_service.get_club_by_id(db, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    club_service.leave_club(db, club_id, current_user.id)
    return {"detail": "Left club"}
