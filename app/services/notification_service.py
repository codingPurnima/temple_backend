from sqlalchemy.orm import Session
from app.models.notification import Notification


def create_notification(db: Session, user_id: int, title: str, message: str, auto_commit: bool= True):
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message
    )
    db.add(notif)
    if auto_commit:
      db.commit()

    return notif      
