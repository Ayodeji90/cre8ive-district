import pytest
from fastapi.testclient import TestClient

from branding_agent.api.app import app
from branding_agent.config import get_settings


@pytest.fixture
def agent_client(monkeypatch):
    monkeypatch.setenv("AI_STUB", "true")
    monkeypatch.setenv("SERVICE_API_KEY", "integration-key")
    get_settings.cache_clear()
    with TestClient(app) as client:
        yield client
    get_settings.cache_clear()


def test_brand_strategy_endpoint_requires_service_key(agent_client):
    response = agent_client.post(
        "/v1/brand/strategy",
        json={"description": "Lagos fashion studio", "industry": "Fashion"},
    )

    assert response.status_code == 401


def test_brand_strategy_endpoint_returns_typed_strategy(agent_client):
    response = agent_client.post(
        "/v1/brand/strategy",
        headers={"X-Agent-Key": "integration-key"},
        json={"description": "Lagos fashion studio", "industry": "Fashion"},
    )

    assert response.status_code == 200
    assert response.json()["primary_name"] == "Your Brand"
    assert response.json()["industry_keywords"][0] == "Fashion"


def test_intake_endpoint_requires_service_key(agent_client):
    response = agent_client.post(
        "/v1/intake/analyze",
        json={"structured_brief": {"core_offering": "Mobile dog grooming"}},
    )

    assert response.status_code == 401


def test_intake_endpoint_normalizes_structured_brief(agent_client):
    response = agent_client.post(
        "/v1/intake/analyze",
        headers={"X-Agent-Key": "integration-key"},
        json={
            "business_id": "biz-123",
            "structured_brief": {
                "business_name": "Paw & Go",
                "core_offering": "Mobile dog grooming",
                "target_audience": "Busy pet owners",
            },
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "ready"
    assert result["normalized_brief"]["business_name"]["source"] == "structured_input"
    assert result["normalized_brief"]["core_offering"]["value"] == "Mobile dog grooming"
    assert result["normalized_brief"]["naming_mode"] == "existing_name"


def test_strategy_package_endpoint_requires_service_key(agent_client):
    response = agent_client.post(
        "/v1/brand/strategy-package",
        json={"brief": {"core_offering": {"value": "Mobile dog grooming"}}},
    )

    assert response.status_code == 401


def test_strategy_package_endpoint_generates_reviewable_package(agent_client):
    response = agent_client.post(
        "/v1/brand/strategy-package",
        headers={"X-Agent-Key": "integration-key"},
        json={
            "brief": {
                "business_name": {
                    "value": "Paw & Go",
                    "source": "structured_input",
                    "evidence": None,
                    "rationale": None,
                },
                "core_offering": {
                    "value": "Mobile dog grooming",
                    "source": "structured_input",
                    "evidence": None,
                    "rationale": None,
                },
                "industry": {
                    "value": "Pet care",
                    "source": "structured_input",
                    "evidence": None,
                    "rationale": None,
                },
                "naming_mode": "existing_name",
            }
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "ready_for_review"
    assert result["strategy"]["primary_name"] == "Paw & Go"
    assert result["validation"]["passed"] is True


def test_intake_endpoint_requests_clarification_when_offering_is_missing(agent_client):
    response = agent_client.post(
        "/v1/intake/analyze",
        headers={"X-Agent-Key": "integration-key"},
        json={"raw_brief": "Paw & Go is a new business."},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "needs_clarification"
    assert result["missing_critical_info"] == ["core_offering"]
    assert result["follow_up_questions"] == ["What product or service will the business provide?"]
