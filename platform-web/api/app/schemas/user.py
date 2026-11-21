import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str | None
    role: str
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None
    role: str = "customer"


class UserUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None


class MeResponse(UserResponse):
    pass
