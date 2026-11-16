import uuid
import pytest
from app.main import app
from app.deps import get_ai
from tests.conftest import auth_headers


class StreamingAIService:
    def __init__(self):
        self.last_new_message = None

    async def respond(self, context, history, message):
        self.last_new_message = message
        if not message:
            yield "Hello! "
            yield "I am Abija, your brand co-founder. "
            yield "What business are we building?"
        elif "launch" in message.lower() or "yes" in message.lower():
            yield "Starting your brand generation now! "
            yield "Hold tight."
        else:
            yield f"I love {message[:25]}! "
            yield "Who is your ideal customer for this?"

    async def extract_context(self, history):
        user_turns = sum(1 for m in history if m["role"] in ("user", "customer"))
        last_content = history[-1]["content"].lower() if history else ""
        confirmed = "launch" in last_content or "yes" in last_content
        has_audience = any("audience" in m["content"].lower() or "creatives" in m["content"].lower() for m in history)
        has_vibe = any("vibrant" in m["content"].lower() or "contemporary" in m["content"].lower() for m in history)
        return {
            "conversation_stage": "complete" if confirmed else "style_preferences" if has_vibe else "target_audience" if has_audience else "business_description",
            "ready_to_generate": confirmed,
            "business_name": "Lagos Bloom",
            "target_audience": "Young urban creatives" if has_audience else None,
            "mood": "Vibrant Afro-contemporary" if has_vibe else None,
            "style_keywords": ["vibrant", "warm", "earthy"] if has_vibe else [],
        }


@pytest.mark.asyncio
async def test_chat_start_with_initial_idea(client, customer):
    fake_ai = StreamingAIService()
    app.dependency_overrides[get_ai] = lambda: fake_ai

    try:
        headers = auth_headers(customer)
        response = await client.post(
            "/api/chat/start",
            json={"initial_idea": "Luxury African botanical skincare formulated in Lagos"},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "conversation_id" in data
        assert "Luxury African" in data["greeting_message"] or "I love" in data["greeting_message"]

        # Check history has both user's initial idea and Abija's response
        history_resp = await client.get(f"/api/chat/{data['conversation_id']}/history", headers=headers)
        assert history_resp.status_code == 200
        history = history_resp.json()
        assert history["total"] == 2
        assert history["messages"][0]["role"] == "customer"
        assert "Luxury African" in history["messages"][0]["content"]
        assert history["messages"][1]["role"] == "assistant"
    finally:
        app.dependency_overrides.pop(get_ai, None)


@pytest.mark.asyncio
async def test_websocket_chat_streaming(customer, session_factory):
    """Exercise WebSocket chat with real streaming chunks."""
    from starlette.testclient import TestClient

    fake_ai = StreamingAIService()
    app.dependency_overrides[get_ai] = lambda: fake_ai

    try:
        # Create a conversation in DB
        from app.models import Conversation
        async with session_factory() as db:
            conv = Conversation(
                user_id=customer.id,
                channel="webchat",
                context={"conversation_stage": "greeting", "ready_to_generate": False},
            )
            db.add(conv)
            await db.commit()
            await db.refresh(conv)
            conv_id = conv.id

        # Use synchronous TestClient for websocket testing
        sync_client = TestClient(app)
        token = auth_headers(customer)["Authorization"].split(" ")[1]
        with sync_client.websocket_connect(f"/api/chat/{conv_id}?token={token}") as ws:
            # 1. First event should be 'ready'
            ready = ws.receive_json()
            assert ready["type"] == "ready"
            assert ready["conversation_id"] == str(conv_id)

            # 2. Ping-pong test
            ws.send_json({"type": "ping"})
            pong = ws.receive_json()
            assert pong["type"] == "pong"

            # 3. Send message and receive streamed chunks + done
            ws.send_json({"content": "We make handmade beaded bags in Lekki"})

            received_chunks = []
            while True:
                msg = ws.receive_json()
                if msg["type"] == "chunk":
                    received_chunks.append(msg["content"])
                elif msg["type"] == "done":
                    assert len(received_chunks) > 0
                    full_text = "".join(received_chunks)
                    assert full_text == msg["content"]
                    assert "context" in msg
                    break

            # 4. Confirmation message triggers ready_to_generate
            ws.send_json({"content": "Yes, launch my brand!"})
            chunks2 = []
            while True:
                msg = ws.receive_json()
                if msg["type"] == "chunk":
                    chunks2.append(msg["content"])
                elif msg["type"] == "done":
                    assert "Starting your brand" in msg["content"]
                    assert msg["context"]["ready_to_generate"] is True
                    break
    finally:
        app.dependency_overrides.pop(get_ai, None)


# ---------------------------------------------------------------------------
# Security tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_websocket_no_token_rejected(customer, session_factory):
    """WebSocket connection without a token must be closed with code 4401."""
    from starlette.testclient import TestClient
    from app.models import Conversation

    async with session_factory() as db:
        conv = Conversation(
            user_id=customer.id,
            channel="webchat",
            context={"conversation_stage": "greeting", "ready_to_generate": False},
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        conv_id = conv.id

    sync_client = TestClient(app)
    with sync_client.websocket_connect(f"/api/chat/{conv_id}") as ws:
        msg = ws.receive()
        assert msg["type"] == "websocket.close"
        assert msg["code"] == 4401


@pytest.mark.asyncio
async def test_websocket_invalid_token_rejected(customer, session_factory):
    """WebSocket connection with a garbage token must be closed with code 4401."""
    from starlette.testclient import TestClient
    from app.models import Conversation

    async with session_factory() as db:
        conv = Conversation(
            user_id=customer.id,
            channel="webchat",
            context={"conversation_stage": "greeting", "ready_to_generate": False},
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        conv_id = conv.id

    sync_client = TestClient(app)
    with sync_client.websocket_connect(f"/api/chat/{conv_id}?token=garbage.token.here") as ws:
        msg = ws.receive()
        assert msg["type"] == "websocket.close"
        assert msg["code"] == 4401


@pytest.mark.asyncio
async def test_websocket_wrong_user_forbidden(session_factory):
    """User B cannot connect to a conversation that belongs to User A — expect 4403."""
    from starlette.testclient import TestClient
    from app.models import Conversation, User
    from jose import jwt
    from app.config import get_settings

    settings = get_settings()

    # Create user A and user B
    user_a = User(id=uuid.uuid4(), email="user_a_ws@example.com", name="User A", role="customer")
    user_b = User(id=uuid.uuid4(), email="user_b_ws@example.com", name="User B", role="customer")
    async with session_factory() as db:
        db.add(user_a)
        db.add(user_b)
        await db.commit()
        await db.refresh(user_a)
        await db.refresh(user_b)
        # Conversation owned by user A
        conv = Conversation(
            user_id=user_a.id,
            channel="webchat",
            context={"conversation_stage": "greeting", "ready_to_generate": False},
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        conv_id = conv.id

    # Mint a valid token for user B
    token_b = jwt.encode(
        {"sub": str(user_b.id), "email": user_b.email, "role": user_b.role},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    sync_client = TestClient(app)
    with sync_client.websocket_connect(f"/api/chat/{conv_id}?token={token_b}") as ws:
        msg = ws.receive()
        assert msg["type"] == "websocket.close"
        assert msg["code"] == 4403


@pytest.mark.asyncio
async def test_history_wrong_user_forbidden(client, session_factory):
    """User B calling GET /{conv_id}/history owned by User A must get HTTP 403."""
    from app.models import Conversation, User
    from jose import jwt
    from app.config import get_settings

    settings = get_settings()

    user_a = User(id=uuid.uuid4(), email="user_a_hist@example.com", name="User A Hist", role="customer")
    user_b = User(id=uuid.uuid4(), email="user_b_hist@example.com", name="User B Hist", role="customer")
    async with session_factory() as db:
        db.add(user_a)
        db.add(user_b)
        await db.commit()
        await db.refresh(user_a)
        await db.refresh(user_b)
        conv = Conversation(
            user_id=user_a.id,
            channel="webchat",
            context={},
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        conv_id = conv.id

    token_b = jwt.encode(
        {"sub": str(user_b.id), "email": user_b.email, "role": user_b.role},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    headers_b = {"Authorization": f"Bearer {token_b}"}
    response = await client.get(f"/api/chat/{conv_id}/history", headers=headers_b)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_start_chat_ignores_user_id_in_body(client, customer):
    """POST /chat/start ignores any user_id in the body; uses the authenticated user."""
    fake_ai = StreamingAIService()
    app.dependency_overrides[get_ai] = lambda: fake_ai

    other_user_id = uuid.uuid4()
    try:
        headers = auth_headers(customer)
        response = await client.post(
            "/api/chat/start",
            # Even if the schema still accepted user_id, it must be ignored
            json={"initial_idea": "Security test idea", "user_id": str(other_user_id)},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        conv_id = data["conversation_id"]

        # Fetch history as the authenticated customer — should succeed
        history_resp = await client.get(f"/api/chat/{conv_id}/history", headers=headers)
        assert history_resp.status_code == 200

        # The conversation must belong to the authenticated user, not other_user_id.
        # We verify by checking that user B (other_user_id) cannot access the history.
        # Since other_user_id may not even exist as a DB user, the conversation owner
        # must be `customer.id`. We confirm it via the successful history fetch above
        # (the ownership check would 403 if ownership were wrong).
        assert conv_id is not None
    finally:
        app.dependency_overrides.pop(get_ai, None)


@pytest.mark.asyncio
async def test_guided_intake_end_to_end_flow(customer, session_factory, monkeypatch):
    """Full Guided Intake with Abija:
    1. Customer provides initial concept and details in conversation.
    2. Abija guides the customer, streams replies, and extracts the brief.
    3. The Business record in the database is continuously updated with the brief.
    4. Upon confirmation (ready_to_generate), business status becomes 'ready' and generation is queued.
    """
    from app.models import Business, Conversation
    from app.services import chat as chat_service

    fake_ai = StreamingAIService()
    app.dependency_overrides[get_ai] = lambda: fake_ai

    async def fake_enqueue(website_id, token):
        return True

    monkeypatch.setattr("app.services.jobs.enqueue_website_job", fake_enqueue)

    try:
        async with session_factory() as db:
            # 1. Start conversation with customer
            conv, greeting = await chat_service.start_conversation(
                db,
                fake_ai,
                user_id=customer.id,
                initial_idea="We handcraft luxury leather bags in Lagos called Lekki Leatherworks.",
            )
            assert conv.business_id is not None
            biz_id = conv.business_id

            # Verify auto-created business is owned by customer and marked onboarding
            biz = await db.get(Business, biz_id)
            assert biz is not None
            assert biz.owner_id == customer.id
            assert biz.status == "onboarding"

            # 2. Turn 1: Customer describes target audience
            chunks1 = []
            async for chunk in chat_service.process_message(
                db,
                None,
                fake_ai,
                conv,
                content="Our target audience is young urban professionals and creatives across Africa.",
            ):
                chunks1.append(chunk)
            assert len(chunks1) > 0

            # Verify business record updated with audience
            await db.refresh(biz)
            assert biz.preferences.get("target_audience") == "Young urban creatives" or biz.preferences.get("target_audience") is not None

            # 3. Turn 2: Customer specifies brand vibe / aesthetic
            chunks2 = []
            async for chunk in chat_service.process_message(
                db,
                None,
                fake_ai,
                conv,
                content="We want a vibrant Afro-contemporary vibe with warm earth tones.",
            ):
                chunks2.append(chunk)
            assert len(chunks2) > 0

            # Verify business preferences updated with mood and style keywords
            await db.refresh(biz)
            assert biz.preferences.get("mood") is not None or biz.preferences.get("style_keywords") is not None

            # 4. Turn 3: Customer confirms launch
            chunks3 = []
            async for chunk in chat_service.process_message(
                db,
                None,
                fake_ai,
                conv,
                content="Yes, launch my brand and deploy my website!",
            ):
                chunks3.append(chunk)
            assert len(chunks3) > 0

            # 5. Verify the complete business brief is persisted in DB
            await db.refresh(conv)
            assert conv.context["ready_to_generate"] is True
            assert conv.context["conversation_stage"] in ("complete", "summary_confirm")

            await db.refresh(biz)
            assert biz.status in ("ready", "active")
            assert biz.name is not None
            assert biz.description is not None
            assert biz.owner_id == customer.id

            # Verify message history contains all user and assistant turns
            msgs, total = await chat_service.list_messages(db, conv.id)
            assert total >= 6
            roles = [m.role for m in msgs]
            assert "customer" in roles
            assert "assistant" in roles
    finally:
        app.dependency_overrides.pop(get_ai, None)
