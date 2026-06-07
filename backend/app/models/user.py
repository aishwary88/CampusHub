from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.database.database import Base


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    ADMIN = "ADMIN"


class AuthProvider(str, Enum):
    GOOGLE = "GOOGLE"
    EMAIL = "EMAIL"
    BOTH = "BOTH"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default=UserRole.STUDENT.value)
    branch = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    profile_photo = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    auth_provider = Column(String(20), nullable=False, default=AuthProvider.EMAIL.value)
    campus_score = Column(Integer, nullable=False, default=0)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    posts = relationship("Post", back_populates="author")
    notifications = relationship("Notification", back_populates="user")
    clubs = relationship("Club", secondary="club_members", back_populates="members")
    events = relationship("Event", secondary="event_attendees", back_populates="attendees")
