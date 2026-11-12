import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    plan: str
    amount: float
    currency: str
    paystack_ref: str | None
    status: str
    deliverables: dict[str, Any]
    paid_at: datetime | None
    fulfilled_at: datetime | None
    created_at: datetime
    updated_at: datetime
