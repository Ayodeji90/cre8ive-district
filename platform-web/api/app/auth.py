"""JWT verification and role-based access control.

Tokens are issued by NextAuth on the frontend and signed with the shared
JWT_SECRET. Expected claims: sub (user id), email, role, iat, exp.
"""

import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_db
from app.logging import get_logger
from app.models import User

log = get_logger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


def decode_token(token: str, settings: Settings) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _claim_uuid(claims: dict) -> uuid.UUID | None:
    for key in ("sub", "user_id", "id"):
        value = claims.get(key)
        if not value:
            continue
        try:
            return uuid.UUID(str(value))
        except ValueError:
            continue
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = decode_token(credentials.credentials, settings)
    user_id = _claim_uuid(claims)
    email = claims.get("email")

    user: User | None = None
    if user_id is not None:
        user = await db.get(User, user_id)
    if user is None and email:
        user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()

    # NextAuth signs users up before the API has ever seen them. Provision the
    # local record on first authenticated request instead of rejecting them.
    if user is None:
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing an identity"
            )
        user = User(
            id=user_id or uuid.uuid4(),
            email=email,
            name=claims.get("name"),
            role=claims.get("role") or "customer",
            avatar_url=claims.get("picture"),
        )
        db.add(user)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            user = (await db.execute(select(User).where(User.email == email))).scalar_one()
        else:
            await db.refresh(user)
            log.info("user_provisioned", user_id=str(user.id), role=user.role)

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User | None:
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db, settings)
    except HTTPException:
        return None


def require_role(*roles: str) -> Callable:
    allowed = set(roles)

    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(sorted(allowed))}",
            )
        return user

    return dependency
