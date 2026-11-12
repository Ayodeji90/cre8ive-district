import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class AdapterUserResponse(BaseModel):
    """Shape expected by the NextAuth adapter's User type."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str | None = None
    image: str | None = None
    emailVerified: datetime | None = None
    role: str = "customer"


class AdapterUserCreate(BaseModel):
    email: EmailStr
    name: str | None = None
    image: str | None = None
    emailVerified: datetime | None = None


class AdapterUserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    image: str | None = None
    emailVerified: datetime | None = None


class AdapterAccountCreate(BaseModel):
    user_id: uuid.UUID
    type: str
    provider: str
    provider_account_id: str
    refresh_token: str | None = None
    access_token: str | None = None
    expires_at: int | None = None
    token_type: str | None = None
    scope: str | None = None
    id_token: str | None = None
    session_state: str | None = None


class AdapterAccountResponse(AdapterAccountCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class VerificationTokenCreate(BaseModel):
    identifier: str
    token: str
    expires: datetime


class VerificationTokenConsume(BaseModel):
    identifier: str
    token: str


class VerificationTokenResponse(VerificationTokenCreate):
    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "AdapterAccountCreate",
    "AdapterAccountResponse",
    "AdapterUserCreate",
    "AdapterUserResponse",
    "AdapterUserUpdate",
    "VerificationTokenConsume",
    "VerificationTokenCreate",
    "VerificationTokenResponse",
]
