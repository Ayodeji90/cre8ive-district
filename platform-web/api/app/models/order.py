from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import JSONType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.review import Review


class Order(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan: Mapped[str] = mapped_column(String(24), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="NGN", nullable=False)
    paystack_ref: Mapped[str | None] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False)
    deliverables: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    business: Mapped[Business] = relationship(back_populates="orders")  # noqa: F821
    reviews: Mapped[list[Review]] = relationship(back_populates="order")  # noqa: F821


__all__ = ["Order"]
