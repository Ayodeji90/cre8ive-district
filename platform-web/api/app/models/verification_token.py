from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class VerificationToken(Base):
    """Single-use magic-link token issued by NextAuth's email provider."""

    __tablename__ = "verification_tokens"

    identifier: Mapped[str] = mapped_column(String(320), primary_key=True)
    token: Mapped[str] = mapped_column(String(255), primary_key=True)
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


__all__ = ["VerificationToken"]
