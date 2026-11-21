"""Credit balance tracking and ledger transaction management."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging import get_logger
from app.models.business import Business
from app.models.credit import CreditTransaction

log = get_logger(__name__)


class InsufficientCreditsError(RuntimeError):
    pass


class BusinessNotFound(LookupError):
    pass


async def get_credit_balance(db: AsyncSession, business_id: uuid.UUID) -> int:
    business = await db.get(Business, business_id)
    if business is None:
        raise BusinessNotFound(f"Business not found: {business_id}")
    return business.credit_balance


async def add_credits(
    db: AsyncSession,
    business_id: uuid.UUID,
    amount: int,
    *,
    transaction_type: str,
    description: str,
    reference_id: str | None = None,
) -> tuple[int, CreditTransaction]:
    """Add credits to business balance and record ledger entry."""
    if amount <= 0:
        raise ValueError("Amount to add must be positive")

    business = await db.scalar(select(Business).where(Business.id == business_id).with_for_update())
    if business is None:
        raise BusinessNotFound(f"Business not found: {business_id}")

    business.credit_balance += amount
    transaction = CreditTransaction(
        business_id=business.id,
        amount=amount,
        balance_after=business.credit_balance,
        transaction_type=transaction_type,
        description=description,
        reference_id=reference_id,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    await db.refresh(business)

    log.info(
        "credits_added",
        business_id=str(business.id),
        amount=amount,
        balance=business.credit_balance,
        type=transaction_type,
    )
    return business.credit_balance, transaction


async def deduct_credits(
    db: AsyncSession,
    business_id: uuid.UUID,
    amount: int,
    *,
    description: str,
    reference_id: str | None = None,
    transaction_type: str = "task_deduction",
) -> tuple[int, CreditTransaction]:
    """Deduct credits from business balance and record ledger entry."""
    if amount <= 0:
        raise ValueError("Amount to deduct must be positive")

    business = await db.scalar(select(Business).where(Business.id == business_id).with_for_update())
    if business is None:
        raise BusinessNotFound(f"Business not found: {business_id}")

    if reference_id:
        prior = await db.scalar(
            select(CreditTransaction).where(
                CreditTransaction.business_id == business_id,
                CreditTransaction.reference_id == reference_id,
                CreditTransaction.transaction_type == transaction_type,
            )
        )
        if prior is not None:
            return business.credit_balance, prior

    if business.credit_balance < amount:
        raise InsufficientCreditsError(
            f"Insufficient credits: balance is {business.credit_balance}, but {amount} required"
        )

    business.credit_balance -= amount
    transaction = CreditTransaction(
        business_id=business.id,
        amount=-amount,
        balance_after=business.credit_balance,
        transaction_type=transaction_type,
        description=description,
        reference_id=reference_id,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    await db.refresh(business)

    log.info(
        "credits_deducted",
        business_id=str(business.id),
        amount=amount,
        balance=business.credit_balance,
        description=description,
    )
    return business.credit_balance, transaction


async def list_transactions(
    db: AsyncSession,
    business_id: uuid.UUID,
    page: int = 1,
    limit: int = 50,
) -> tuple[list[CreditTransaction], int]:
    total = (
        await db.execute(
            select(func.count())
            .select_from(CreditTransaction)
            .where(CreditTransaction.business_id == business_id)
        )
    ).scalar_one()

    result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.business_id == business_id)
        .order_by(CreditTransaction.created_at.desc(), CreditTransaction.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return list(result.scalars().all()), total
