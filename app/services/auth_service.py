from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.crud.user import get_user_by_email, create_user
from app.core.security import hash_password, verify_password
from app.core.security import create_access_token, create_refresh_token

def register_user(db: Session, name, email, password):
    existing = get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail= "Email already exists")
    hashed = hash_password(password)
    return create_user(db, name, email, hashed)

def login_user(db: Session, email, password):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    
    access_token= create_access_token({
        "user_id": user.id,
        "role": user.role.value
    })

    refresh_token= create_refresh_token({
        "user_id": user.id,
    })

    user.refresh_token= refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id
    }