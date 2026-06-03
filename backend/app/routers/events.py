from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.user import User
from app.schemas.event import EventCreate, EventRead
from app.services import event_service
from app.auth.jwt import get_current_user

router = APIRouter()

@router.get("/", response_model=List[EventRead])
def get_events(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return event_service.get_events(db, skip=skip, limit=limit)

@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/", response_model=EventRead, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return event_service.create_event(db, event, organizer_id=current_user.id)

@router.post("/{event_id}/rsvp", status_code=200)
def rsvp_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event_service.rsvp_event(db, event_id, current_user.id)
    return {"detail": "RSVP successful"}

@router.delete("/{event_id}/rsvp", status_code=200)
def cancel_rsvp(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event_service.cancel_rsvp(db, event_id, current_user.id)
    return {"detail": "RSVP cancelled"}
