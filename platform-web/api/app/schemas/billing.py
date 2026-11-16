from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class CreditBalanceResponse(BaseModel):
    business_id: uuid.UUID
    balance: int


class CreditDeductRequest(BaseModel):
    amount: int = Field(gt=0, description="Number of credits to deduct")
    description: str
    reference_id: str | None = None


class CreditDeductResponse(BaseModel):
    business_id: uuid.UUID
    amount_deducted: int
    new_balance: int
    transaction_id: uuid.UUID


class CreditTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    amount: int
    balance_after: int
    transaction_type: str
    description: str
    reference_id: str | None = None
    created_at: datetime


class CreditLedgerResponse(BaseModel):
    business_id: uuid.UUID
    balance: int
    transactions: list[CreditTransactionResponse]
    total: int
    page: int
    limit: int
