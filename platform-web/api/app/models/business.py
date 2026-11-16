from __future__ import annotations

import uuid as _uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import JSONType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.credit import CreditTransaction
    from app.models.order import Order
    from app.models.user import User


class Business(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "businesses"

    # Every business must have an owner — the authenticated user who created it.
    owner_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(String(80))
    location: Mapped[str | None] = mapped_column(String(120))
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    contact_email: Mapped[str | None] = mapped_column(String(200))
    plan: Mapped[str] = mapped_column(String(24), default="free", nullable=False)
    credit_balance: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="onboarding", nullable=False)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)

    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])  # noqa: F821

    brands: Mapped[list["Brand"]] = relationship(  # noqa: F821
        back_populates="business", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(  # noqa: F821
        back_populates="business", cascade="all, delete-orphan"
    )
    credit_transactions: Mapped[list["CreditTransaction"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )


__all__ = ["Business"]
