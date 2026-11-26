#!/usr/bin/env python3
"""Real PostgreSQL concurrent verification of resume_or_start_chat.

Two concurrent HTTP requests hit POST /api/businesses/{business_id}/chat/resume.
Both must return the same conversation_id, and the database must contain exactly
one new conversation row for that business/user pair.

If the API is not already listening on :8000, this script starts uvicorn itself.
PostgreSQL must be running (docker compose -f platform-web/docker-compose.yml start postgres).

Run from the repo root with the api venv python:

    python3 platform-web/api/scripts/test_concurrent_chat_resume.py
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
import uuid

import asyncpg

API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Import the API's own config so we sign JWTs with the same secret the API
# verifies against (including any .env it may have loaded via pydantic-settings).
sys.path.insert(0, API_DIR)
try:
    from app.config import Settings

    _settings = Settings()
    JWT_SECRET = _settings.JWT_SECRET
    JWT_ALGORITHM = _settings.JWT_ALGORITHM
    print(f"Loaded JWT_SECRET from API config (len={len(JWT_SECRET)})")
except Exception as exc:
    print(f"WARNING: could not load API config for JWT secret: {type(exc).__name__}: {exc}")
    print("  Falling back to env JWT_SECRET; the test will likely get 401.")
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-secret-change-me")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://cre8ive:localdev@127.0.0.1:5432/cre8ive"
)
API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")

# A unique phrase we inject as initial_idea so we can confirm idea-preservation.
INITIAL_IDEA = f"Concurrent test idea {uuid.uuid4().hex[:12]}"


def make_token(user_id: uuid.UUID, email: str) -> str:
    import jwt

    return jwt.encode(
        {"sub": str(user_id), "email": email, "role": "customer"},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


async def setup_data(conn: asyncpg.Connection, business_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Clean any prior conversations/slots for this business/owner pair."""
    await conn.execute(
        "DELETE FROM new_conv_slots WHERE business_id = $1 AND owner_id = $2",
        business_id,
        user_id,
    )
    await conn.execute(
        "UPDATE conversations SET status = 'closed' WHERE business_id = $1 AND user_id = $2",
        business_id,
        user_id,
    )


def _http_post(url: str, headers: dict, body_bytes: bytes) -> dict:
    """Single synchronous HTTP POST using urllib (its own TCP connection)."""
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen

    req = Request(url, method="POST", headers=headers, data=body_bytes)
    try:
        with urlopen(req, timeout=30) as resp:
            return {"status": resp.status, "body": json.loads(resp.read().decode())}
    except HTTPError as exc:
        raw = exc.read().decode() if exc.fp else "{}"
        try:
            body = json.loads(raw)
        except ValueError:
            body = {"raw": raw}
        return {"status": exc.code, "body": body}
    except Exception as exc:
        return {"status": -1, "body": {"error": f"{type(exc).__name__}: {exc}"}}


async def concurrent_verify() -> tuple[bool, str]:
    token = None
    business_id = None
    user_id = None
    conn: asyncpg.Connection | None = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)

        # -- Create user and business --
        user_id = uuid.uuid4()
        business_id = uuid.uuid4()
        await conn.execute(
            """INSERT INTO users (id, email, name, role, created_at, updated_at)
               VALUES ($1, $2, $3, 'customer', now(), now())""",
            user_id,
            f"test-{user_id.hex[:8]}@example.com",
            "Concurrent Test User",
        )
        await conn.execute(
            """INSERT INTO businesses
               (id, name, slug, description, industry, location, contact_phone,
                contact_email, plan, credit_balance, status, preferences, owner_id,
                created_at, updated_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'active', $11, $12, now(), now())""",
            business_id,
            "Concurrent Biz",
            f"concurrent-biz-{user_id.hex[:8]}",
            "A business for concurrent resume testing",
            None,
            None,
            None,
            None,
            "free",
            50,
            "{}",  # preferences is NOT NULL (JSON column)
            user_id,
        )

        await setup_data(conn, business_id, user_id)

        token = make_token(user_id, f"test-{user_id.hex[:8]}@example.com")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        url = f"{API_BASE}/api/businesses/{business_id}/chat/resume"

        # Both callers send the same initial_idea so we can verify it persists
        # exactly once (on the single created conversation).
        # Try JSON body first; fall back to query parameter if the endpoint
        # expects initial_idea as a query param.
        async def fire(idx: int) -> dict:
            # Send initial_idea as a JSON body field via the ChatResumeRequest
            # Pydantic model (initial_idea is optional, so {} is also valid).
            payload = json.dumps({"initial_idea": INITIAL_IDEA}).encode()
            h = {**headers, "Content-Length": str(len(payload))}
            return await asyncio.to_thread(_http_post, url, h, payload)

        results = await asyncio.gather(fire(0), fire(1))

        r0, r1 = results[0], results[1]

        if r0["status"] != 200 or r1["status"] != 200:
            return False, (
                f"Non-200 response(s): r0={r0['status']} {r0['body']}, "
                f"r1={r1['status']} {r1['body']}"
            )

        c0 = r0["body"].get("conversation_id")
        c1 = r1["body"].get("conversation_id")
        if not c0 or not c1:
            return False, f"Missing conversation_id: r0={r0['body']}, r1={r1['body']}"

        if c0 != c1:
            return False, f"Different conversation IDs: r0={c0}, r1={c1}"

        # -- Verify exactly one conversation exists for this business/user --
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM conversations WHERE business_id = $1 AND user_id = $2 AND status IN ('active','idle')",
            business_id,
            user_id,
        )
        cnt = int(row["cnt"])
        if cnt != 1:
            return False, f"Expected 1 active/idle conversation, got {cnt}"

        # -- Verify the slot carries the same conversation_id --
        slot_row = await conn.fetchrow(
            "SELECT conversation_id FROM new_conv_slots WHERE business_id = $1 AND owner_id = $2",
            business_id,
            user_id,
        )
        if slot_row is None:
            return False, "No new_conv_slots row for this business/owner pair"
        slot_conv_raw = slot_row["conversation_id"]
        if isinstance(slot_conv_raw, uuid.UUID):
            slot_conv = slot_conv_raw
        elif isinstance(slot_conv_raw, str):
            slot_conv = uuid.UUID(slot_conv_raw)
        else:
            slot_conv = uuid.UUID(str(slot_conv_raw))
        if slot_conv != uuid.UUID(c0):
            return False, f"Slot conversation_id {slot_conv} differs from returned {c0}"

        c0_uuid = uuid.UUID(c0)

        # -- Verify the initial_idea was persisted exactly once --
        # The idea should appear as the first inbound message in the single
        # conversation that was created.
        msgs = await conn.fetch(
            "SELECT content, role, direction FROM messages WHERE conversation_id = $1 ORDER BY created_at ASC",
            c0_uuid,
        )
        idea_seen = False
        for m in msgs:
            content = (m["content"] or "").strip()
            if content == INITIAL_IDEA.strip():
                if m["role"] != "customer" or m["direction"] != "inbound":
                    return False, (f"initial_idea found but with wrong role/direction: {dict(m)}")
                if idea_seen:
                    return False, (f"initial_idea appears more than once in conversation {c0_uuid}")
                idea_seen = True
        if not idea_seen:
            return False, (
                f"initial_idea '{INITIAL_IDEA}' not found in any message of conversation {c0_uuid}. "
                f"Messages: {[dict(m) for m in msgs]}"
            )

        return True, (
            f"PASS: both callers got conversation_id={c0_uuid}, 1 conversation in DB, "
            f"initial_idea persisted exactly once"
        )

    except Exception as exc:
        return False, f"Exception: {type(exc).__name__}: {exc}"
    finally:
        if conn is not None:
            await conn.close()


async def main() -> int:
    print("Concurrent chat resume verification")
    print(f"  DB: {DATABASE_URL}")
    print(f"  API: {API_BASE}")
    print(f"  initial_idea: {INITIAL_IDEA}")
    print()

    # Probe the API first. If it is not listening, start uvicorn ourselves.
    uvicorn_proc: subprocess.Popen[str] | None = None
    api_listening = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", 8000))
            api_listening = True
        except OSError:
            api_listening = False

    if not api_listening:
        print("API not listening on :8000 — starting uvicorn now")
        uvicorn_proc = subprocess.Popen(  # noqa: ASYNC220
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--log-level",
                "info",
            ],
            cwd=API_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 30
        while time.time() < deadline:
            if uvicorn_proc.poll() is not None:
                print(f"uvicorn exited early with rc {uvicorn_proc.returncode}")
                return 1
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                try:
                    s.connect(("127.0.0.1", 8000))
                    break
                except OSError:
                    time.sleep(0.3)  # noqa: ASYNC251
        else:
            print("timed out waiting for uvicorn to listen")
            return 1
        print("uvicorn listening")

    try:
        ok, msg = await concurrent_verify()
    finally:
        if uvicorn_proc is not None and uvicorn_proc.poll() is None:
            uvicorn_proc.terminate()
            try:
                uvicorn_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                uvicorn_proc.kill()

    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
