from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.user import User, UserRole
from app.services.role_service import require_role
from app.schemas.user import UserOut

router = APIRouter(tags=["admin"])


@router.post("/make-admin/{user_id}")
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role([UserRole.SUPER_ADMIN]))
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role== UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=400, detail= "Cannot modify Super Admin")

    user.role = UserRole.ADMIN
    db.commit()

    return {"message": "User promoted to ADMIN"}
# all users will first register themselves as normal users, super_admin will promote them to admin.


@router.get("/users", response_model=list[UserOut])
def get_all_users(
    db: Session= Depends(get_db),
    current_user= Depends(require_role([UserRole.SUPER_ADMIN]))
):
    users= db.query(User).all()
    return users