import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BusinessCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=100)
    description: str | None = None
    industry: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: str | None = Field(default=None, max_length=200)
    preferences: dict[str, Any] = Field(default_factory=dict)


class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    industry: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: str | None = Field(default=None, max_length=200)
    plan: str | None = None
    status: str | None = None
    preferences: dict[str, Any] | None = None


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    industry: str | None
    location: str | None
    contact_phone: str | None
    contact_email: str | None
    plan: str
    status: str
    preferences: dict[str, Any]
    created_at: datetime
    updated_at: datetime
