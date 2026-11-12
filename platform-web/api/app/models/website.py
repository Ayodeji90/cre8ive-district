import uuid
from typing import Any

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import JSONType, TimestampMixin, UUIDMixin


class Website(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "websites"

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


__all__ = ["Website"]
