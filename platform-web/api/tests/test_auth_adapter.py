from datetime import UTC, datetime, timedelta

import pytest

ADAPTER = {"X-Auth-Adapter-Secret": "test-secret"}


@pytest.mark.asyncio
async def test_adapter_requires_secret(client):
    response = await client.post("/api/auth/adapter/users", json={"email": "x@example.com"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_and_lookup_user(client):
    created = await client.post(
        "/api/auth/adapter/users",
        headers=ADAPTER,
        json={"email": "new@example.com", "name": "New User", "image": "https://img.test/a.png"},
    )
    assert created.status_code == 200
    user = created.json()
    assert user["email"] == "new@example.com"
    assert user["role"] == "customer"
    assert user["image"] == "https://img.test/a.png"
    assert user["emailVerified"] is None

    again = await client.post(
        "/api/auth/adapter/users",
        headers=ADAPTER,
        json={"email": "new@example.com", "name": "New User"},
    )
    assert again.json()["id"] == user["id"]

    lookup = await client.get(
        "/api/auth/adapter/users/lookup", headers=ADAPTER, params={"email": "new@example.com"}
    )
    assert lookup.status_code == 200
    assert lookup.json()["id"] == user["id"]

    missing = await client.get(
        "/api/auth/adapter/users/lookup", headers=ADAPTER, params={"email": "nobody@example.com"}
    )
    assert missing.status_code == 200
    assert missing.json() is None

    updated = await client.patch(
        f"/api/auth/adapter/users/{user['id']}",
        headers=ADAPTER,
        json={"name": "Renamed"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Renamed"


@pytest.mark.asyncio
async def test_verification_token_is_single_use(client):
    expires = (datetime.now(UTC) + timedelta(hours=24)).isoformat()
    payload = {"identifier": "magic@example.com", "token": "first-token", "expires": expires}

    created = await client.post(
        "/api/auth/adapter/verification-tokens", headers=ADAPTER, json=payload
    )
    assert created.status_code == 200

    consumed = await client.post(
        "/api/auth/adapter/verification-tokens/consume", headers=ADAPTER, json=payload
    )
    assert consumed.status_code == 200
    assert consumed.json()["token"] == "first-token"

    replayed = await client.post(
        "/api/auth/adapter/verification-tokens/consume", headers=ADAPTER, json=payload
    )
    assert replayed.status_code == 200
    assert replayed.json() is None

    # A newer link invalidates the previous one for the same email.
    await client.post(
        "/api/auth/adapter/verification-tokens", headers=ADAPTER, json=payload
    )
    second = {**payload, "token": "second-token"}
    await client.post(
        "/api/auth/adapter/verification-tokens", headers=ADAPTER, json=second
    )
    old = await client.post(
        "/api/auth/adapter/verification-tokens/consume", headers=ADAPTER, json=payload
    )
    assert old.json() is None
    new = await client.post(
        "/api/auth/adapter/verification-tokens/consume", headers=ADAPTER, json=second
    )
    assert new.json()["token"] == "second-token"


@pytest.mark.asyncio
async def test_link_and_find_oauth_account(client):
    user = (
        await client.post(
            "/api/auth/adapter/users",
            headers=ADAPTER,
            json={"email": "google@example.com"},
        )
    ).json()

    account = {
        "user_id": user["id"],
        "type": "oauth",
        "provider": "google",
        "provider_account_id": "google-123",
        "access_token": "token",
        "expires_at": 1900000000,
        "token_type": "bearer",
        "scope": "openid email profile",
    }
    linked = await client.post("/api/auth/adapter/accounts", headers=ADAPTER, json=account)
    assert linked.status_code == 200
    assert linked.json()["provider_account_id"] == "google-123"

    # Linking the same provider account again updates instead of duplicating.
    relinked = await client.post(
        "/api/auth/adapter/accounts",
        headers=ADAPTER,
        json={**account, "access_token": "refreshed"},
    )
    assert relinked.status_code == 200
    assert relinked.json()["id"] == linked.json()["id"]
    assert relinked.json()["access_token"] == "refreshed"

    found = await client.get(
        "/api/auth/adapter/accounts",
        headers=ADAPTER,
        params={"provider": "google", "provider_account_id": "google-123"},
    )
    assert found.status_code == 200
    assert found.json()["user_id"] == user["id"]
