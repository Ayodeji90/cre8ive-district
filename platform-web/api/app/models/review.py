from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.order import Order


class Review(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reviews"

    order_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("orders.id", ondelete="SET NULL"), index=True
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("brands.id", ondelete="CASCADE"), index=True
    )
    website_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("websites.id", ondelete="SET NULL")
    )
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    brand: Mapped[Brand | None] = relationship(back_populates="reviews")  # noqa: F821
    order: Mapped[Order | None] = relationship(back_populates="reviews")  # noqa: F821


__all__ = ["Review"]
