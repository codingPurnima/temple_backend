from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.event import EventCreate,EventOut, ParticipantResponse
from app.models.event import Event
from app.services.role_service import require_role
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from app.models.event_registration import EventRegistration, RegistrationStatus
from app.services.notification_service import create_notification

router = APIRouter(tags=["events"])


@router.post("/create", response_model=EventOut, status_code=201)
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    try:
        event= Event(**data.model_dump(), created_by= user.id)
        db.add(event)
        db.flush()

        users= db.query(User.id).all()
        for u in users:
            create_notification(
                db, 
                u.id,
                "New Event Created",
                f"{event.title} has been announced!", 
                auto_commit=False
            )
        db.commit()
        db.refresh(event)
        return event
    
    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create event"
        )

@router.post("/{event_id}/join")
def join_event(
    event_id: int,
    db: Session= Depends(get_db),
    user= Depends(require_role([UserRole.NORMAL, UserRole.PREMIUM]))
):
    try:
        # check event exists
        event = db.get(Event, event_id)
        if not event:
            raise HTTPException(404, "Event not found")

        # check already registered
        existing = db.query(EventRegistration).filter_by(
            user_id=user.id,
            event_id=event_id
        ).first()

        if existing:
            raise HTTPException(400, "Already registered")
        
        # count confirmed users
        confirmed_count = db.query(EventRegistration).filter_by(
            event_id=event_id,
            status=RegistrationStatus.CONFIRMED
        ).count()
        # decide status
        if not event.capacity or event.capacity==0 or confirmed_count < event.capacity:
            status = RegistrationStatus.CONFIRMED
        else:
            status = RegistrationStatus.WAITLISTED

        reg = EventRegistration(
            user_id=user.id,
            event_id=event_id,
            status=status
        )

        db.add(reg)
        db.flush()

        create_notification(
            db,
            user.id,
            "Event Registration",
            f"You have been {status.value} for {event.title}",
            auto_commit=False
        )
        db.commit()

        return {"status": status.value}
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to join event"
        )

@router.delete("/{event_id}/leave")
def leave_event(
    event_id: int, 
    db: Session= Depends(get_db),
    user= Depends(require_role([UserRole.NORMAL, UserRole.PREMIUM]))
):
    try:
        event = db.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        reg = db.query(EventRegistration).filter_by(
            user_id=user.id,
            event_id=event_id
        ).first()

        if not reg:
            raise HTTPException(status_code=404, detail="Event not found")

        was_confirmed = reg.status == RegistrationStatus.CONFIRMED

        db.delete(reg)

        create_notification(
            db,
            user.id,
            "Event Update",
            f"You have left {event.title} ",
            auto_commit=False
        )

        # promote waitlisted user
        if was_confirmed:
            next_user = (db.query(EventRegistration)
            .filter_by(
                event_id=event_id,
                status=RegistrationStatus.WAITLISTED
            )
            .order_by(EventRegistration.id.asc())
            .first()
            )

            if next_user:
                next_user.status = RegistrationStatus.CONFIRMED

                create_notification(
                    db,
                    next_user.user_id,
                    "You're In!",
                    "You have been moved from waitlist to confirmed",
                    auto_commit=False
                )
        db.commit()

        return {"message": "Left event"}
    
    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to leave event"
        )

@router.get("/{event_id}/participants", response_model=list[ParticipantResponse])
def get_participants(
    event_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    event = db.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    
    regs = db.query(EventRegistration).filter_by(event_id=event_id).all()

    return regs
