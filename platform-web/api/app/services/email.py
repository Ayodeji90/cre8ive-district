"""Transactional email via Resend's HTTP API."""

from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.logging import get_logger

log = get_logger(__name__)

RESEND_URL = "https://api.resend.com/emails"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailError(RuntimeError):
    pass


async def _post_email(*, api_key: str, payload: dict) -> str | None:
    if not api_key:
        raise EmailError("RESEND_API_KEY is not configured")

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                RESEND_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise EmailError("Could not reach Resend") from exc

    if response.status_code >= 400:
        log.error("resend_error", status=response.status_code, body=response.text)
        raise EmailError("Resend rejected the email")

    return response.json().get("id")


async def send_brand_ready_email(
    *,
    api_key: str,
    sender: str,
    to: str,
    business_name: str,
    tagline: str,
    download_url: str,
) -> str | None:
    html = _env.get_template("email_brand_ready.html").render(
        business_name=business_name,
        tagline=tagline,
        download_url=download_url,
    )
    payload = {
        "from": sender,
        "to": [to],
        "subject": f"Your brand kit is ready — {business_name}",
        "html": html,
    }

    email_id = await _post_email(api_key=api_key, payload=payload)
    log.info("brand_email_sent", to=to, email_id=email_id)
    return email_id


async def send_waitlist_confirmation_email(
    *,
    api_key: str,
    sender: str,
    to: str,
    site_url: str,
) -> str | None:
    html = _env.get_template("email_waitlist_confirmation.html").render(site_url=site_url)
    payload = {
        "from": sender,
        "to": [to],
        "subject": "You're on the Cre8ive District waitlist",
        "html": html,
    }

    email_id = await _post_email(api_key=api_key, payload=payload)
    log.info("waitlist_email_sent", to=to, email_id=email_id)
    return email_id
