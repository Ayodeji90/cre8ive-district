import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.brand import WebsiteResponse
from app.schemas.business import BusinessResponse
from app.schemas.order import OrderResponse


class ReviewCreate(BaseModel):
    brand_id: uuid.UUID | None = None
    order_id: uuid.UUID | None = None
    website_id: uuid.UUID | None = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID | None
    brand_id: uuid.UUID | None
    website_id: uuid.UUID | None
    reviewer_id: uuid.UUID | None
    status: str
    notes: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ReviewListItem(BaseModel):
    id: uuid.UUID
    brand_id: uuid.UUID | None
    order_id: uuid.UUID | None
    business_id: uuid.UUID | None
    business_name: str | None
    brand_thumbnail: str | None
    status: str
    reviewer_id: uuid.UUID | None
    created_at: datetime


class ReviewDetail(ReviewResponse):
    brand: dict[str, Any] | None = None
    business: BusinessResponse | None = None
    order: OrderResponse | None = None
    website: WebsiteResponse | None = None
    conversation: dict[str, Any] | None = None


class RevisionRequest(BaseModel):
    notes: str = Field(min_length=1)


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1)
