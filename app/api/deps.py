from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.deps import get_db
from app.models.user import User
from app.models.roles import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "access":
            raise  HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def require_admin(user: User = Depends(get_current_user)):
    if user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user