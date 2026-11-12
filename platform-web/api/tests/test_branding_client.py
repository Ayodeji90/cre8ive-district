import httpx
import pytest

from app.llm.remote import BrandingAgentClient
from app.schemas.ai import BrandStrategy


@pytest.mark.asyncio
async def test_branding_agent_client_validates_strategy_response():
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/brand/strategy"
        assert request.headers["X-Agent-Key"] == "test-key"
        return httpx.Response(
            200,
            json={
                "primary_name": "Test Studio",
                "name_alternatives": [],
                "positioning": "A distinct studio",
                "tagline": "Made with care",
                "voice_attributes": ["warm", "direct", "bold"],
                "brand_story": "A team began with a clear idea and a community.",
                "elevator_pitch": "A studio serving its community.",
                "target_description": "Local customers",
                "industry_keywords": [],
            },
        )

    client = BrandingAgentClient(
        "http://branding-agent",
        "test-key",
        transport=httpx.MockTransport(respond),
    )

    strategy = await client.generate_strategy("A studio", "Design", {})

    assert isinstance(strategy, BrandStrategy)
    assert strategy.primary_name == "Test Studio"
