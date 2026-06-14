import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, Boolean, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id: Mapped[str] = mapped_column(String, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    # acquisition | onboarding | adoption | life_event | orchestrator
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. lead_scored | outreach_sent | kyc_started | account_created | nudge_sent | life_event_detected
    message_sent: Mapped[str | None] = mapped_column(Text, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0.0 - 1.0
    stage_before: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stage_after: Mapped[str | None] = mapped_column(String(50), nullable=True)
    was_overridden: Mapped[bool] = mapped_column(Boolean, default=False)
    override_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    override_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    llm_raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
