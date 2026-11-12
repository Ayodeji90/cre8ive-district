import uuid

from pydantic import BaseModel, EmailStr


class DeliveryRequest(BaseModel):
    email: EmailStr | None = None


class DeliveryResponse(BaseModel):
    order_id: uuid.UUID
    status: str
    email_id: str | None = None
    download_url: str | None = None
