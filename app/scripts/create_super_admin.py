from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

db = SessionLocal()

admin = User(
    name="Jai Jai",
    email="jaijai@girdharlal.com",
    password_hash=hash_password("vrindavan"),
    role=UserRole.SUPER_ADMIN
)

db.add(admin)
db.commit()

print("Super admin created")