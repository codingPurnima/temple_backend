from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.db.database import Base
from app.models.roles import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid= Column(
        String(128), unique=True, index=True, nullable= False
    )
    name = Column(String(100), nullable= False)
    email = Column(String(100), unique=True, index=True, nullable= False)
    role = Column(Enum(UserRole), default=UserRole.NORMAL)
    is_verified = Column(Boolean, default=False)