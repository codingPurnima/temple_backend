from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_user
from app.models.notification import Notification
from app.services.role_service import require_role
from app.models.roles import UserRole

router = APIRouter(tags=["notifications"])

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    notifs = db.query(Notification).filter_by(
        user_id=user.id
    ).order_by(Notification.created_at.desc()).all()

    return notifs


@router.post("/{notif_id}/read")
def mark_read(
    notif_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    notif = db.query(Notification).filter(
        Notification.id==notif_id,
        Notification.user_id==user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notif:
        notif.is_read = True
        db.commit()

    return {"message": "notification read"}