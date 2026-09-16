from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_current_user
from app.schemas.user import ProfileCreate, UserLogin, UserCreate
from app.services.auth_service import register_user, login_user
from app.db.deps import get_db
from app.core.config import settings
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from app.schemas.token import RefreshRequest
from app.services.role_service import require_role
from app.models.roles import UserRole

from app.api.deps import get_firebase_user

router = APIRouter(tags=["Auth"])

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "name": user.name
    }

@router.post("/profile")
def create_profile(
    data: ProfileCreate, 
    firebase_user= Depends(get_firebase_user), 
    db:Session= Depends(get_db)
):
    firebase_uid= firebase_user["uid"]
    email= firebase_user.get("email")

    existing= db.query(User).filter(
        User.firebase_uid== firebase_uid
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User profile already exists"
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

@router.get("/admin-only")
def admin_route(
    user= Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    return {"message": "Welcome Admin"}

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = register_user(db, data.name, data.email, data.password)
        return {"message": "User created", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm= Depends(), db: Session = Depends(get_db)):
    email= form_data.username
    pwd= form_data.password
    try:
        result = login_user(db, email, pwd)
        return {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer",
            "user_id": result["user_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/logout")
def logout(user=Depends(get_current_user), db: Session = Depends(get_db)):
    user.refresh_token = None
    db.commit()
    return {"message": "Logged out"}
    
@router.post("/refresh")
def refresh_token(data: RefreshRequest, db: Session= Depends(get_db)):
    try:
        payload = decode_refresh_token(data.refresh_token)

        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()

        if not user or user.refresh_token != data.refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # generate new access token
        new_access_token = create_access_token({
            "user_id": user.id,
            "role": user.role.value
        })
        new_refresh_token= create_refresh_token({
            "user_id": user.id
        })
        user.refresh_token= new_refresh_token
        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")