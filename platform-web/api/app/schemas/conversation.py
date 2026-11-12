import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatStartRequest(BaseModel):
    user_id: uuid.UUID | None = None
    business_id: uuid.UUID | None = None


class ChatStartResponse(BaseModel):
    conversation_id: uuid.UUID
    greeting_message: str
    context: dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    direction: str
    content: str
    media_url: str | None
    media_type: str | None
    role: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    conversation_id: uuid.UUID
    messages: list[MessageResponse]
    context: dict[str, Any]
    total: int
    page: int
    limit: int


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID | None
    user_id: uuid.UUID | None
    channel: str
    external_id: str | None
    phone_number: str | None
    status: str
    context: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ConversationCreate(BaseModel):
    business_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    channel: str = "webchat"
    external_id: str | None = None
    phone_number: str | None = None


class InboundMessage(BaseModel):
    content: str = Field(min_length=1)
    media_url: str | None = None
    media_type: str | None = None
