from sqlalchemy import Column, Integer, String, Text
from app.db.database import Base

class Lyrics(Base):
    __tablename__ = "lyrics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # full lyrics here
    author= Column(String(50), nullable=True)