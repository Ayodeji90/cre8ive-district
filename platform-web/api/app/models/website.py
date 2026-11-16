import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import JSONType, TimestampMixin, UUIDMixin


class Website(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "websites"
    __table_args__ = (Index("ix_websites_status_updated_at", "status", "updated_at"),)

    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("brands.id", ondelete="SET NULL")
    )
    deployment_url: Mapped[str | None] = mapped_column(String(500))
    custom_domain: Mapped[str | None] = mapped_column(String(200))
    vercel_id: Mapped[str | None] = mapped_column(String(100))
    pages: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list, nullable=False)
    lighthouse: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    status: Mapped[str] = mapped_column(String(24), default="generating", nullable=False)
    job_token: Mapped[str | None] = mapped_column(String(36), index=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)


__all__ = ["Website"]
