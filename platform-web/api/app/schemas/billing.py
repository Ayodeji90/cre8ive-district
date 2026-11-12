import uuid

from pydantic import BaseModel, EmailStr


class BillingInitializeRequest(BaseModel):
    plan: str
    business_id: uuid.UUID
    email: EmailStr


class BillingInitializeResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str
    amount: float
    currency: str = "NGN"


class BillingVerifyResponse(BaseModel):
    reference: str
    status: str
    order_id: uuid.UUID | None = None
