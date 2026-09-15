from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(
        to_encode,
        settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def create_refresh_token(data: dict):
    to_encode= data.copy()
    expire= datetime.utcnow()+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(
        to_encode, 
        settings.REFRESH_TOKEN_SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )

def decode_refresh_token(token: str):
    try:
        payload= jwt.decode(token, settings.REFRESH_TOKEN_SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type")!= "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        return payload
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")