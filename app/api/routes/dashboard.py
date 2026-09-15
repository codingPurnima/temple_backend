from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.event import Event
from app.models.event_registration import EventRegistration
from app.models.notification import Notification
from datetime import date

router = APIRouter(tags=["dashboard"])

@router.get("/")
def get_dashboard(
    db: Session= Depends(get_db),
    user: User= Depends(get_current_user)
):
    
    my_event_ids = select(EventRegistration.event_id).where(
        EventRegistration.user_id== user.id
    )

    upcoming_events = db.query(Event).filter(
        Event.start_date > date.today()
    ).order_by(Event.start_date).limit(15).all()

    my_events = db.query(Event).filter(
        Event.id.in_(my_event_ids)
    ).all()

    notifications = db.query(Notification).filter_by(
        user_id=user.id
    ).order_by(Notification.created_at.desc()).limit(15).all()

    unread_count = db.query(Notification).filter_by(
        user_id=user.id,
        is_read=False
    ).count()

    enriched_events=[]

    for event in upcoming_events:
        reg= db.query(EventRegistration).filter_by(
            user_id= user.id,
            event_id= event.id
        ).first()
        enriched_events.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "capacity": event.capacity,
            "start_date": event.start_date,
            "end_date": event.end_date,

            "is_registered": reg is not None,
            "registration_status": reg.status.value if reg else None
        })

    return {
        "upcoming_events": enriched_events,
        "my_events": my_events,
        "notifications": notifications,
        "unread_count": unread_count
    }