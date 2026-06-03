from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventCreate(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    club_id: Optional[int] = None

class EventRead(BaseModel):
    id: int
    title: str
    description: str
    location: Optional[str]
    start_time: datetime
    end_time: datetime
    club_id: Optional[int]
    organizer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
