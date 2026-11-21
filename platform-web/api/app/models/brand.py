from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import JSONType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.review import Review


class Brand(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "brands"

    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    strategy: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    logo_urls: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list, nullable=False)
    colors: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    fonts: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    copy: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    guidelines_pdf: Mapped[str | None] = mapped_column(String(500))
    kit_zip_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(24), default="generating", nullable=False)

    business: Mapped[Business] = relationship(back_populates="brands")  # noqa: F821
    reviews: Mapped[list[Review]] = relationship(  # noqa: F821
        back_populates="brand", cascade="all, delete-orphan"
    )


__all__ = ["Brand"]
