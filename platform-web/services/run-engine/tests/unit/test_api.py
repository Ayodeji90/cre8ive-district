from uuid import uuid4

import httpx
import pytest

from run_engine.api.app import app


@pytest.mark.asyncio
async def test_api_health_check():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "run-engine"


@pytest.mark.asyncio
async def test_api_run_lifecycle():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Start a run
        payload = {
            "business_id": str(uuid4()),
            "user_id": str(uuid4()),
            "credits_budget": 50,
            "goal": "Test run lifecycle",
            "max_iterations": 1,
        }
        res = await client.post("/v1/runs", json=payload)
        assert res.status_code == 201
        run_data = res.json()
        run_id = run_data["id"]

        # Check status
        res_get = await client.get(f"/v1/runs/{run_id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == run_id

        # Check brief
        res_brief = await client.get(f"/v1/runs/{run_id}/brief")
        assert res_brief.status_code == 200
        assert res_brief.json()["run_id"] == run_id
