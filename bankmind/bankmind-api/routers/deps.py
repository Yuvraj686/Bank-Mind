"""Shared auth dependency for protected routes."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from jose import jwt, JWTError

from database import get_db
from models.banker import Banker
from config import get_settings

settings = get_settings()
security = HTTPBearer()


def get_current_banker(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Banker:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        banker_id: str = payload.get("sub")
        if banker_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    banker = db.get(Banker, banker_id)
    if banker is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Banker not found")

    return banker
