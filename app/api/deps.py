from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.deps import get_db
from app.models.user import User
from app.models.roles import UserRole

from app import firebase
from firebase_admin import auth
from app.core import firebase
from firebase_admin.exceptions import FirebaseError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_firebase_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        decoded_token = auth.verify_id_token(token)

        print("Firebase token verified")
        print("UID:", decoded_token.get("uid"))
        print("Email:", decoded_token.get("email"))

        return decoded_token

    except Exception as e:
        print("FIREBASE TOKEN ERROR:", repr(e))

        raise HTTPException(
            status_code=401,
            detail=f"Firebase token verification failed: {str(e)}"
        )

def get_current_user(
    firebase_user= Depends(get_firebase_user),
    db: Session = Depends(get_db)
):
    firebase_uid= firebase_user.get("uid")
    user= db.query(User).filter(
        User.firebase_uid== firebase_uid
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found")

    return user

def require_admin(user: User = Depends(get_current_user)):
    if user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user