"""
SQLite DB initializer — creates all tables directly from models (bypasses Alembic).
Used when DATABASE_URL starts with sqlite://
Run: python init_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, Base
from models import Banker, Customer, ProductEligibility, Transaction, Conversation, AgentLog  # noqa
import uuid
import bcrypt
from sqlalchemy.orm import Session
from config import get_settings

settings = get_settings()

def init():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    # Seed demo banker
    with Session(engine) as db:
        from sqlalchemy import select
        existing = db.execute(select(Banker).where(Banker.email == settings.demo_banker_email)).scalar_one_or_none()
        if not existing:
            password_hash = bcrypt.hashpw(settings.demo_banker_password.encode(), bcrypt.gensalt(rounds=12)).decode()
            banker = Banker(
                id=str(uuid.uuid4()),
                name="Demo Banker",
                email=settings.demo_banker_email,
                password_hash=password_hash,
                role="admin",
            )
            db.add(banker)
            db.commit()
            print(f"Demo banker created: {settings.demo_banker_email} / {settings.demo_banker_password}")
        else:
            print(f"Demo banker already exists: {settings.demo_banker_email}")

    print("[OK] Database initialized successfully!")
    print(f"   Login: {settings.demo_banker_email} / {settings.demo_banker_password}")

if __name__ == "__main__":
    init()
