from pydantic import BaseModel, EmailStr
from app.core.config import settings

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True