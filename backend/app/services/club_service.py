from sqlalchemy.orm import Session
from app.models.club import Club, club_members
from app.schemas.club import ClubCreate


def get_clubs(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Club).offset(skip).limit(limit).all()


def get_club_by_id(db: Session, club_id: int):
    return db.query(Club).filter(Club.id == club_id).first()


def create_club(db: Session, club: ClubCreate, president_id: int):
    db_club = Club(
        name=club.name,
        description=club.description,
        category=club.category,
        president_id=president_id,
    )
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club


def join_club(db: Session, club_id: int, user_id: int):
    stmt = club_members.insert().values(user_id=user_id, club_id=club_id)
    try:
        db.execute(stmt)
        db.commit()
    except Exception:
        db.rollback()


def leave_club(db: Session, club_id: int, user_id: int):
    stmt = club_members.delete().where(
        club_members.c.user_id == user_id,
        club_members.c.club_id == club_id,
    )
    db.execute(stmt)
    db.commit()
