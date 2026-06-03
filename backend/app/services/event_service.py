from sqlalchemy.orm import Session
from app.models.event import Event, event_attendees
from app.schemas.event import EventCreate


def get_events(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Event).offset(skip).limit(limit).all()


def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()


def create_event(db: Session, event: EventCreate, organizer_id: int):
    db_event = Event(
        title=event.title,
        description=event.description,
        location=event.location,
        start_time=event.start_time,
        end_time=event.end_time,
        club_id=event.club_id,
        organizer_id=organizer_id,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def rsvp_event(db: Session, event_id: int, user_id: int):
    stmt = event_attendees.insert().values(user_id=user_id, event_id=event_id)
    try:
        db.execute(stmt)
        db.commit()
    except Exception:
        db.rollback()


def cancel_rsvp(db: Session, event_id: int, user_id: int):
    stmt = event_attendees.delete().where(
        event_attendees.c.user_id == user_id,
        event_attendees.c.event_id == event_id,
    )
    db.execute(stmt)
    db.commit()
