from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_firebase_user
from app.db.deps import get_db
from app.models.user import User
from app.models.roles import UserRole
from app.schemas.user import ProfileCreate
from app.services.role_service import require_role

router = APIRouter(tags=["Auth"])

@router.get("/me")
def get_me(
    user: User = Depends(get_current_user),
):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "name": user.name,
        "is_verified": user.is_verified,
    }


@router.get("/admin-only")
def admin_route(
    user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
    ),
):
    return {
        "message": "Welcome Admin"
    }

@router.post("/profile")
def create_profile(
    data: ProfileCreate, 
    firebase_user= Depends(get_firebase_user), 
    db:Session= Depends(get_db)
):
    firebase_uid= firebase_user.get("uid")
    email= firebase_user.get("email")

    if not firebase_uid or not email:
        raise HTTPException(status_code=400, detail= "Invalid Firebase user data")

    existing= db.query(User).filter(
        User.firebase_uid== firebase_uid
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User profile already exists"
        )

    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="A profile already exists for this email",
        )

    user = User(
        firebase_uid=firebase_uid,
        name=data.name,
        email=email,
        role=UserRole.NORMAL,
        is_verified=firebase_user.get("email_verified", False)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Profile created",
        "user_id": user.id
    }