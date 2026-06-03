from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    id: int
    name: Optional[str]
    email: EmailStr
    role: str
    branch: Optional[str]
    year: Optional[int]
    profile_photo: Optional[str]
    bio: Optional[str]
    campus_score: int
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
