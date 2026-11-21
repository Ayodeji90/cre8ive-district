from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class WaitlistSignup(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "waitlist_signups"

    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)
    business_description: Mapped[str | None] = mapped_column(String(1000), nullable=True)


__all__ = ["WaitlistSignup"]
