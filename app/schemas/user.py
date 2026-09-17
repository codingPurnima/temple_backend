from pydantic import BaseModel, EmailStr
from app.core.config import settings

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_verified: bool

    class Config:
        from_attributes = True

class ProfileCreate(BaseModel):
    name: str