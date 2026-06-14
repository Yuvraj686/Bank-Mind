import uuid
from datetime import datetime, date
from typing import Any
from sqlalchemy import String, DateTime, Integer, Float, Boolean, Date, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    occupation: Mapped[str] = mapped_column(String(255), nullable=False)
    income_monthly: Mapped[float] = mapped_column(Float, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Website / digital behavior
    website_visits: Mapped[int] = mapped_column(Integer, default=0)
    pages_viewed: Mapped[str | None] = mapped_column(String(500), nullable=True)  # comma-separated

    # Lifecycle
    stage: Mapped[str] = mapped_column(String(50), default="lead")  # lead | onboarding | active | dormant
    lead_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    kyc_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending | verified | failed
    kyc_attempts: Mapped[int] = mapped_column(Integer, default=0)
    account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Features
    features_adopted: Mapped[Any] = mapped_column(JSON, default=dict)
    # e.g. {"upi": false, "sip": false, "fd": false, "credit_card": false, "home_loan": false}

    # Life-event tracking
    last_life_event_detected: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_life_event_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Orchestrator lock
    currently_processing: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
