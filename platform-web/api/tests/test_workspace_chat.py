"""Tests for Business-keyed workspace state and chat resume/start.

Covers:
 - Workspace state response structure
 - Conversation priority selection (active > idle > closed)
 - Chat resume returns same conversation
 - Chat resume reactivates idle conversation
 - Ownership enforcement — user cannot access another user's business
 - Concurrent resume requests (simulated sequential since SQLite doesn't
   support FOR UPDATE, but validates the response schema)
"""

import uuid

import pytest
from sqlalchemy import select

from app.models import Business, Conversation, User
from tests.conftest import auth_headers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_user(session_factory, email: str, name: str = "User") -> User:
    user = User(id=uuid.uuid4(), email=email, name=name, role="customer")
    async with session_factory() as db:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def _create_business(session_factory, owner_id: uuid.UUID, name: str, slug: str) -> Business:
    biz = Business(
        id=uuid.uuid4(),
        name=name,
        slug=slug,
        plan="free",
        credit_balance=50,
        owner_id=owner_id,
    )
    async with session_factory() as db:
        db.add(biz)
        await db.commit()
        await db.refresh(biz)
    return biz


async def _create_conversation(
    session_factory,
    business_id: uuid.UUID,
    user_id: uuid.UUID,
    status: str = "active",
) -> Conversation:
    convo = Conversation(
        id=uuid.uuid4(),
        business_id=business_id,
        user_id=user_id,
        status=status,
        context={},
    )
    async with session_factory() as db:
        db.add(convo)
        await db.commit()
        await db.refresh(convo)
    return convo


# ---------------------------------------------------------------------------
# Workspace State Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_workspace_state_returns_business_data(client, session_factory, customer):
    biz = await _create_business(session_factory, customer.id, "Aso Dye Studio", "aso-dye-studio")
    headers = auth_headers(customer)

    res = await client.get(f"/api/businesses/{biz.id}/state", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["business_id"] == str(biz.id)
    assert data["name"] == "Aso Dye Studio"
    assert data["credit_balance"] == 50
    assert data["plan"] == "free"
    assert data["conversation"] is None  # no conversations yet
    assert data["pending_approvals"] == 0


@pytest.mark.asyncio
async def test_workspace_state_prefers_active_over_idle(client, session_factory, customer):
    """Active conversation should be selected even if an idle one exists."""
    biz = await _create_business(session_factory, customer.id, "Priority Biz", "priority-biz")

    # Create idle conversation first
    await _create_conversation(session_factory, biz.id, customer.id, status="idle")
    # Then create active conversation
    active_convo = await _create_conversation(session_factory, biz.id, customer.id, status="active")

    headers = auth_headers(customer)
    res = await client.get(f"/api/businesses/{biz.id}/state", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["conversation"] is not None
    assert data["conversation"]["id"] == str(active_convo.id)
    assert data["conversation"]["status"] == "active"


@pytest.mark.asyncio
async def test_workspace_state_prefers_active_over_closed(client, session_factory, customer):
    """Active conversation should be selected over closed ones."""
    biz = await _create_business(
        session_factory, customer.id, "Closed Check Biz", "closed-check-biz"
    )

    # Create closed conversation first
    await _create_conversation(session_factory, biz.id, customer.id, status="closed")
    # Then create active conversation
    active_convo = await _create_conversation(session_factory, biz.id, customer.id, status="active")

    headers = auth_headers(customer)
    res = await client.get(f"/api/businesses/{biz.id}/state", headers=headers)
    assert res.status_code == 200

    convo = res.json()["conversation"]
    assert convo["id"] == str(active_convo.id)
    assert convo["status"] == "active"


@pytest.mark.asyncio
async def test_workspace_state_prefers_idle_over_closed(client, session_factory, customer):
    """Idle conversation should be preferred over closed."""
    biz = await _create_business(session_factory, customer.id, "Idle Check Biz", "idle-check-biz")

    await _create_conversation(session_factory, biz.id, customer.id, status="closed")
    idle_convo = await _create_conversation(session_factory, biz.id, customer.id, status="idle")

    headers = auth_headers(customer)
    res = await client.get(f"/api/businesses/{biz.id}/state", headers=headers)
    assert res.status_code == 200

    convo = res.json()["conversation"]
    assert convo["id"] == str(idle_convo.id)
    assert convo["status"] == "idle"


# ---------------------------------------------------------------------------
# Chat Resume Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_resume_creates_new_conversation(client, session_factory, customer):
    biz = await _create_business(session_factory, customer.id, "Fresh Chat Biz", "fresh-chat-biz")
    headers = auth_headers(customer)

    res = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["mode"] == "new"
    assert "conversation_id" in data
    assert data["greeting_message"] is not None
    assert isinstance(data["context"], dict)


@pytest.mark.asyncio
async def test_chat_resume_returns_same_conversation(client, session_factory, customer):
    """Two consecutive resume calls should return the same conversation."""
    biz = await _create_business(session_factory, customer.id, "Resume Biz", "resume-biz")
    headers = auth_headers(customer)

    # First call — creates a new conversation
    res1 = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["mode"] == "new"

    # Second call — should resume the same conversation
    res2 = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["mode"] == "resumed"
    assert data2["conversation_id"] == data1["conversation_id"]


@pytest.mark.asyncio
async def test_chat_resume_never_returns_none_response(client, session_factory, customer):
    """resume_or_start_chat must return a valid ChatResumeResponse on every
    non-error branch, including the new-conversation path."""
    biz = await _create_business(session_factory, customer.id, "None Check Biz", "none-check-biz")
    headers = auth_headers(customer)

    res = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "conversation_id" in data
    assert "mode" in data
    assert data["mode"] in ("new", "resumed")


@pytest.mark.asyncio
async def test_chat_resume_reactivates_idle_conversation(client, session_factory, customer):
    """An idle conversation should be reactivated to 'active' on resume."""
    biz = await _create_business(session_factory, customer.id, "Idle Resume Biz", "idle-resume-biz")

    idle_convo = await _create_conversation(session_factory, biz.id, customer.id, status="idle")

    headers = auth_headers(customer)
    res = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["mode"] == "resumed"
    assert data["conversation_id"] == str(idle_convo.id)

    # Verify it's now active in the workspace state
    state_res = await client.get(f"/api/businesses/{biz.id}/state", headers=headers)
    convo = state_res.json()["conversation"]
    assert convo["status"] == "active"


@pytest.mark.asyncio
async def test_chat_resume_replaces_stale_slot_when_conversation_closed(
    client, session_factory, customer
):
    """If the new-conversation slot points at a conversation that was later
    closed (and no other active/idle conversation exists), resume must not
    return the stale ID — it should clear the slot and create a fresh
    conversation."""
    from app.models import NewConvSlot

    biz = await _create_business(
        session_factory, customer.id, "Stale Slot Biz", "stale-slot-biz"
    )

    # Create a closed conversation and preseed the slot with its id so the
    # slot points at a non-resumable conversation — the exact shape the
    # stale-slot guard protects against. There must be no other
    # active/idle conversation for this business, or step 1 would resume
    # that one instead.
    stale_convo = await _create_conversation(
        session_factory, biz.id, customer.id, status="closed"
    )
    async with session_factory() as db:
        await db.execute(
            NewConvSlot.__table__.insert().values(
                business_id=biz.id,
                owner_id=customer.id,
                conversation_id=stale_convo.id,
            )
        )
        await db.commit()

    headers = auth_headers(customer)
    res = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Must create a new conversation, not return the stale closed one.
    assert data["mode"] == "new"
    assert data["conversation_id"] != str(stale_convo.id)

    # The stale slot must no longer point at the closed conversation.
    async with session_factory() as db:
        slot_row = (
            await db.execute(
                select(NewConvSlot.conversation_id).where(
                    NewConvSlot.business_id == biz.id,
                    NewConvSlot.owner_id == customer.id,
                )
            )
        ).scalars().first()
    assert slot_row != stale_convo.id
    # After creating a new conversation the slot is preseeded with its id.
    assert slot_row == uuid.UUID(data["conversation_id"])


@pytest.mark.asyncio
async def test_chat_resume_skips_closed_conversation(client, session_factory, customer):
    """A closed conversation should not be resumed — a new one should be created."""
    biz = await _create_business(
        session_factory, customer.id, "Closed Resume Biz", "closed-resume-biz"
    )

    closed_convo = await _create_conversation(session_factory, biz.id, customer.id, status="closed")

    headers = auth_headers(customer)
    res = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Should create a new conversation since the existing one is closed
    assert data["mode"] == "new"
    assert data["conversation_id"] != str(closed_convo.id)


@pytest.mark.asyncio
# ---------------------------------------------------------------------------
# Ownership Enforcement Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_workspace_state_rejects_non_owner(client, session_factory, customer):
    """A user should not be able to access another user's workspace state."""
    other_user = await _create_user(session_factory, "other@example.com", "Other")
    biz = await _create_business(session_factory, other_user.id, "Other Biz", "other-biz")

    # customer tries to access other_user's business
    headers = auth_headers(customer)
    res = await client.get(f"/api/businesses/{biz.id}/state", headers=headers)
    assert res.status_code in (403, 404)


@pytest.mark.asyncio
async def test_chat_resume_rejects_non_owner(client, session_factory, customer):
    """A user should not be able to resume chat on another user's business."""
    other_user = await _create_user(session_factory, "rival@example.com", "Rival")
    biz = await _create_business(session_factory, other_user.id, "Rival Biz", "rival-biz")

    headers = auth_headers(customer)
    res = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res.status_code in (403, 404)


# ---------------------------------------------------------------------------
# Concurrent Resume Tests (simulated)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_resume_produces_valid_responses(client, session_factory, customer):
    """Two rapid resume requests should both return valid ChatResumeResponse
    structures.  On SQLite (test environment), FOR UPDATE is a no-op, but
    we still validate that both responses have the correct schema and that
    at most one is 'new'.
    """
    biz = await _create_business(session_factory, customer.id, "Concurrent Biz", "concurrent-biz")
    headers = auth_headers(customer)

    # Fire two sequential requests (can't truly test concurrent with ASGI test client)
    res1 = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    res2 = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)

    assert res1.status_code == 200
    assert res2.status_code == 200

    d1, d2 = res1.json(), res2.json()

    # Both should have required fields
    for d in (d1, d2):
        assert "conversation_id" in d
        assert "mode" in d
        assert d["mode"] in ("new", "resumed")
        assert isinstance(d.get("context", {}), dict)

    # First is new, second should be resumed with same id
    assert d1["mode"] == "new"
    assert d2["mode"] == "resumed"
    assert d2["conversation_id"] == d1["conversation_id"]


# ---------------------------------------------------------------------------
# Response Schema Validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_resume_response_schema(client, session_factory, customer):
    """Verify the response matches the ChatResumeResponse Pydantic schema."""
    biz = await _create_business(session_factory, customer.id, "Schema Biz", "schema-biz")
    headers = auth_headers(customer)
    res = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Required fields present
    assert "conversation_id" in data
    assert "mode" in data
    assert "context" in data

    # greeting_message present for new conversations
    if data["mode"] == "new":
        assert "greeting_message" in data

    # No unexpected raw dict fields (should be a proper serialized response)
    uuid.UUID(data["conversation_id"])  # validates it's a proper UUID string


@pytest.mark.asyncio
async def test_chat_resume_response_always_serializable(client, session_factory, customer):
    """Every resume response body should round-trip through the declared
    response model without ResponseValidationError."""
    biz = await _create_business(
        session_factory, customer.id, "Serialization Biz", "serialization-biz"
    )
    headers = auth_headers(customer)
    res = await client.post(f"/api/businesses/{biz.id}/chat/resume", headers=headers)
    assert res.status_code == 200
    data = res.json()
    # Basic structural sanity — ChatResumeResponse fields
    assert isinstance(data.get("context"), dict)
    assert isinstance(uuid.UUID(data["conversation_id"]), uuid.UUID)
    assert data["mode"] in ("new", "resumed")
