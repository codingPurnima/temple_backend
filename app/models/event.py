from sqlalchemy import Column, Integer, String, ForeignKey, Date
from app.db.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)

    capacity = Column(Integer, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"))

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)