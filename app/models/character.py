from sqlalchemy import Column, Integer, String, Text
from app.db.database import Base

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    image_url = Column(String(500))  # Firebase link