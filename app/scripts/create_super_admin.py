from app.db.database import SessionLocal
from app.models.user import User, UserRole
from firebase_admin import auth
from app.core import firebase

from app.core.config import settings
db = SessionLocal()

email= settings.SUPER_ADMIN_EMAIL
password= settings.SUPER_ADMIN_PASSWORD
name= settings.SUPER_ADMIN_NAME

try:
    firebase_user= auth.create_user(
        email= email,
        password= password,
        display_name= name,
        email_verified= True
    )

    print("Firebase user created.")
    print("Firebase UID:", firebase_user.uid)

    admin= User(
        firebase_uid= firebase_user.uid,
        name= name,
        email= email,
        role= UserRole.SUPER_ADMIN,
        is_verified= True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    print("Super admin created successfully")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()