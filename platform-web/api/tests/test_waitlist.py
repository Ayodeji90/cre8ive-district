import respx
from httpx import Response
from sqlalchemy import func, select

from app.config import Settings
from app.deps import get_app_settings
from app.main import app
from app.models import WaitlistSignup


async def _count_signups(session_factory) -> int:
    async with session_factory() as db:
        return (await db.execute(select(func.count(WaitlistSignup.id)))).scalar_one()


async def test_join_waitlist_stores_signup(client, session_factory):
    response = await client.post(
        "/api/waitlist", json={"email": "Ada@Example.com", "source": "hero"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "already_joined": False,
        "confirmation_sent": False,
    }

    async with session_factory() as db:
        signups = (await db.execute(select(WaitlistSignup))).scalars().all()

    assert [signup.email for signup in signups] == ["ada@example.com"]
    assert signups[0].source == "hero"


async def test_join_waitlist_is_idempotent(client, session_factory):
    payload = {"email": "ada@example.com", "source": "hero"}
    await client.post("/api/waitlist", json=payload)
    response = await client.post("/api/waitlist", json={**payload, "source": "footer"})

    assert response.status_code == 200
    assert response.json()["already_joined"] is True
    assert await _count_signups(session_factory) == 1


async def test_join_waitlist_ignores_honeypot(client, session_factory):
    response = await client.post(
        "/api/waitlist",
        json={"email": "bot@example.com", "company": "Spam Inc"},
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert await _count_signups(session_factory) == 0


async def test_join_waitlist_rejects_invalid_email(client, session_factory):
    response = await client.post("/api/waitlist", json={"email": "not-an-email"})

    assert response.status_code == 422
    assert await _count_signups(session_factory) == 0


@respx.mock
async def test_join_waitlist_sends_confirmation_email(client):
    resend_route = respx.post("https://api.resend.com/emails").mock(
        return_value=Response(200, json={"id": "email_123"})
    )
    app.dependency_overrides[get_app_settings] = lambda: Settings(
        RESEND_API_KEY="re_test",
        EMAIL_FROM="Cre8ive District <brands@example.com>",
    )

    response = await client.post("/api/waitlist", json={"email": "ada@example.com"})

    assert response.status_code == 200
    assert response.json()["confirmation_sent"] is True
    assert resend_route.called
    payload = resend_route.calls.last.request.content.decode()
    assert "ada@example.com" in payload
    assert "waitlist" in payload.lower()


@respx.mock
async def test_signup_is_kept_when_email_fails(client, session_factory):
    respx.post("https://api.resend.com/emails").mock(
        return_value=Response(500, text="resend down")
    )
    app.dependency_overrides[get_app_settings] = lambda: Settings(
        RESEND_API_KEY="re_test",
        EMAIL_FROM="Cre8ive District <brands@example.com>",
    )

    response = await client.post("/api/waitlist", json={"email": "ada@example.com"})

    assert response.status_code == 200
    assert response.json()["confirmation_sent"] is False
    assert await _count_signups(session_factory) == 1
