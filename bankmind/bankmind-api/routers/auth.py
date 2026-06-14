"""Auth router — login and profile endpoints."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
import bcrypt
from jose import jwt

from database import get_db
from models.banker import Banker
from config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    banker: dict


def create_token(banker_id: str, email: str) -> str:
    payload = {
        "sub": banker_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiry_hours),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    banker = db.execute(
        select(Banker).where(Banker.email == request.email)
    ).scalar_one_or_none()

    if not banker:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not bcrypt.checkpw(request.password.encode(), banker.password_hash.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Update last login
    banker.last_login_at = datetime.utcnow()
    db.commit()

    token = create_token(banker.id, banker.email)

    return LoginResponse(
        access_token=token,
        banker={
            "id": banker.id,
            "name": banker.name,
            "email": banker.email,
            "role": banker.role,
        }
    )


@router.get("/me")
def get_me(db: Session = Depends(get_db), banker_id: str = Depends(lambda: None)):
    """Returns current banker profile — protected by JWT middleware in main.py."""
    return {"message": "Use the JWT middleware to get current user"}
