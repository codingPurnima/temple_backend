from sqlalchemy import Column, Integer, ForeignKey, Enum
from app.db.database import Base
import enum

 
class RegistrationStatus(enum.Enum):
    CONFIRMED = "CONFIRMED"
    WAITLISTED = "WAITLISTED"


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))

    status = Column(Enum(RegistrationStatus))