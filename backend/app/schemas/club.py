from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClubCreate(BaseModel):
    name: str
    description: str
    category: Optional[str] = None

class ClubRead(BaseModel):
    id: int
    name: str
    description: str
    category: Optional[str]
    president_id: int
    created_at: datetime

    class Config:
        from_attributes = True
