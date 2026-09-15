from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import date
from typing import Optional


class EventCreate(BaseModel):
    title: str= Field(min_length=1, max_length=255)
    description: Optional[str] = None
    capacity: Optional[int]= Field(default=None, ge=0)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
    
class EventOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    capacity: Optional[int]
    start_date: date
    end_date: date
    created_by: int

    model_config = ConfigDict(from_attributes=True)

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ParticipantResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    
    model_config = ConfigDict(from_attributes=True)