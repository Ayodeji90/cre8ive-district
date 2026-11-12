"""Persistence endpoints for the NextAuth adapter.

NextAuth runs in the Next.js app and calls these routes server-to-server with a
shared secret. They store OAuth accounts and single-use magic-link tokens so the
frontend never needs a second database.
"""

import secrets
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_db
from app.models import Account, User, VerificationToken
from app.schemas.auth_adapter import (
    AdapterAccountCreate,
    AdapterAccountResponse,
    AdapterUserCreate,
    AdapterUserResponse,
    AdapterUserUpdate,
    VerificationTokenConsume,
    VerificationTokenCreate,
    VerificationTokenResponse,
)

router = APIRouter(prefix="/auth/adapter", tags=["auth-adapter"], include_in_schema=False)


def require_adapter_secret(
    x_auth_adapter_secret: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    expected = settings.AUTH_ADAPTER_SECRET or settings.JWT_SECRET
    if not x_auth_adapter_secret or not secrets.compare_digest(
        x_auth_adapter_secret, expected
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid adapter secret"
        )


def to_adapter_user(user: User) -> AdapterUserResponse:
    return AdapterUserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        image=user.avatar_url,
        emailVerified=None,
        role=user.role,
    )


async def find_user_by_email(db: AsyncSession, email: str) -> User | None:
    return (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()


@router.post(
    "/users",
    response_model=AdapterUserResponse,
    dependencies=[Depends(require_adapter_secret)],
)
async def create_user(payload: AdapterUserCreate, db: AsyncSession = Depends(get_db)):
    existing = await find_user_by_email(db, payload.email)
    if existing is not None:
        return to_adapter_user(existing)

    user = User(
        email=payload.email,
        name=payload.name,
        role="customer",
        avatar_url=payload.image,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return to_adapter_user(user)


@router.get(
    "/users/lookup",
    response_model=AdapterUserResponse | None,
    dependencies=[Depends(require_adapter_secret)],
)
async def get_user_by_email(
    email: str = Query(min_length=3), db: AsyncSession = Depends(get_db)
):
    user = await find_user_by_email(db, email)
    return to_adapter_user(user) if user else None


@router.get(
    "/users/{user_id}",
    response_model=AdapterUserResponse | None,
    dependencies=[Depends(require_adapter_secret)],
)
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    return to_adapter_user(user) if user else None


@router.patch(
    "/users/{user_id}",
    response_model=AdapterUserResponse,
    dependencies=[Depends(require_adapter_secret)],
)
async def update_user(
    user_id: uuid.UUID,
    payload: AdapterUserUpdate,
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.email is not None and payload.email != user.email:
        clash = await find_user_by_email(db, payload.email)
        if clash is not None:
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = payload.email
    if "name" in payload.model_fields_set:
        user.name = payload.name
    if "image" in payload.model_fields_set:
        user.avatar_url = payload.image
    await db.commit()
    await db.refresh(user)
    return to_adapter_user(user)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_adapter_secret)],
)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    user = await db.get(User, user_id)
    if user is not None:
        await db.delete(user)
        await db.commit()


@router.post(
    "/accounts",
    response_model=AdapterAccountResponse,
    dependencies=[Depends(require_adapter_secret)],
)
async def link_account(payload: AdapterAccountCreate, db: AsyncSession = Depends(get_db)):
    existing = (
        await db.execute(
            select(Account).where(
                Account.provider == payload.provider,
                Account.provider_account_id == payload.provider_account_id,
            )
        )
    ).scalar_one_or_none()

    values = payload.model_dump()
    if existing is not None:
        for key, value in values.items():
            setattr(existing, key, value)
        await db.commit()
        await db.refresh(existing)
        return existing

    account = Account(**values)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get(
    "/accounts",
    response_model=AdapterAccountResponse | None,
    dependencies=[Depends(require_adapter_secret)],
)
async def get_account_by_provider(
    provider: str,
    provider_account_id: str,
    db: AsyncSession = Depends(get_db),
):
    return (
        await db.execute(
            select(Account).where(
                Account.provider == provider,
                Account.provider_account_id == provider_account_id,
            )
        )
    ).scalar_one_or_none()


@router.post(
    "/verification-tokens",
    response_model=VerificationTokenResponse,
    dependencies=[Depends(require_adapter_secret)],
)
async def create_verification_token(
    payload: VerificationTokenCreate, db: AsyncSession = Depends(get_db)
):
    # A new magic link invalidates any earlier outstanding link for this email.
    await db.execute(
        delete(VerificationToken).where(
            VerificationToken.identifier == payload.identifier
        )
    )
    token = VerificationToken(
        identifier=payload.identifier,
        token=payload.token,
        expires=payload.expires,
    )
    db.add(token)
    await db.commit()
    return token


@router.post(
    "/verification-tokens/consume",
    response_model=VerificationTokenResponse | None,
    dependencies=[Depends(require_adapter_secret)],
)
async def consume_verification_token(
    payload: VerificationTokenConsume, db: AsyncSession = Depends(get_db)
):
    token = (
        await db.execute(
            select(VerificationToken).where(
                VerificationToken.identifier == payload.identifier,
                VerificationToken.token == payload.token,
            )
        )
    ).scalar_one_or_none()
    if token is None:
        return None

    stored = VerificationTokenResponse.model_validate(token)
    await db.delete(token)
    await db.commit()

    expires = stored.expires
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires < datetime.now(UTC):
        return None
    return stored


__all__ = ["router"]
