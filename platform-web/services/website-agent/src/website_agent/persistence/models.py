from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SiteJobModel(Base):
    __tablename__ = "site_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="generating", index=True)
    files_json: Mapped[dict] = mapped_column(JSON, default=dict)
    spec_json: Mapped[dict] = mapped_column(JSON, default=dict)
    quality_json: Mapped[dict] = mapped_column(JSON, default=dict)
    deployment_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
