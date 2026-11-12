from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db import get_db
from app.deps import get_app_settings
from app.logging import get_logger
from app.models import WaitlistSignup
from app.schemas.waitlist import WaitlistJoinRequest, WaitlistJoinResponse
from app.services.email import EmailError, send_waitlist_confirmation_email

log = get_logger(__name__)
router = APIRouter(prefix="/waitlist", tags=["waitlist"])


@router.post("", response_model=WaitlistJoinResponse)
async def join_waitlist(
    payload: WaitlistJoinRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> WaitlistJoinResponse:
    # Honeypot: pretend the submission worked without storing or emailing.
    if payload.company:
        return WaitlistJoinResponse()

    email = payload.email.strip().lower()
    existing = (
        await db.execute(select(WaitlistSignup.id).where(WaitlistSignup.email == email))
    ).first()
    if existing is not None:
        return WaitlistJoinResponse(already_joined=True)

    signup = WaitlistSignup(email=email, source=payload.source.strip().lower() or "unknown")
    db.add(signup)
    try:
        await db.commit()
    except IntegrityError:
        # Another request inserted the same email between our lookup and commit.
        await db.rollback()
        return WaitlistJoinResponse(already_joined=True)

    confirmation_sent = False
    if settings.RESEND_API_KEY:
        try:
            await send_waitlist_confirmation_email(
                api_key=settings.RESEND_API_KEY,
                sender=settings.EMAIL_FROM,
                to=email,
                site_url=settings.MARKETING_URL.rstrip("/"),
            )
            confirmation_sent = True
        except EmailError:
            # The signup is already saved; a failed email must not lose it.
            log.warning("waitlist_confirmation_failed", email=email, exc_info=True)
    else:
        log.info("waitlist_confirmation_skipped", reason="RESEND_API_KEY is not configured")

    return WaitlistJoinResponse(confirmation_sent=confirmation_sent)
