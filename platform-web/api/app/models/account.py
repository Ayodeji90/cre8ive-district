from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Account(UUIDMixin, TimestampMixin, Base):
    """OAuth account linked to a user (Google, etc.)."""

    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint(
            "provider", "provider_account_id", name="uq_accounts_provider_account"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    access_token: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[int | None]
    token_type: Mapped[str | None] = mapped_column(String(64))
    scope: Mapped[str | None] = mapped_column(Text)
    id_token: Mapped[str | None] = mapped_column(Text)
    session_state: Mapped[str | None] = mapped_column(String(255))

    user: Mapped[User] = relationship(back_populates="accounts")


__all__ = ["Account"]
