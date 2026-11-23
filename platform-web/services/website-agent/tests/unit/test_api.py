import httpx
import pytest

from website_agent.api.app import app


@pytest.mark.asyncio
async def test_api_health():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["service"] == "website-agent"


@pytest.mark.asyncio
async def test_api_generate_and_deploy_website():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "brand": {
                "name": "Zaria Botanicals",
                "tagline": "Pure Organic Skincare",
                "palette": {
                    "primary": "#2D5A3D",
                    "secondary": "#8B6914",
                    "accent": "#D4A853",
                },
            },
            "business": {
                "name": "Zaria Botanicals",
                "description": "Organic shea butter and cold-pressed oils from Northern Nigeria.",
                "industry": "Beauty & Wellness",
                "location": "Kaduna, Nigeria",
                "whatsapp_number": "2348033445566",
            },
        }

        # Test generate
        gen_res = await client.post("/v1/websites/generate", json=payload)
        assert gen_res.status_code == 201
        gen_data = gen_res.json()
        site_id = gen_data["site_id"]
        assert len(gen_data["pages"]) == 4
        assert gen_data["quality"]["passed"] is True

        # Test preview page
        preview_res = await client.get(f"/v1/websites/{site_id}/preview/index")
        assert preview_res.status_code == 200
        assert "Zaria Botanicals" in preview_res.text

        # Test deploy
        deploy_res = await client.post("/v1/websites/deploy", json={"site_id": site_id})
        assert deploy_res.status_code == 200
        deploy_data = deploy_res.json()
        assert deploy_data["site_id"] == site_id
        assert deploy_data["ready_state"] == "READY"
        assert "zaria-botanicals.cre8ivedistrict.app" in deploy_data["live_url"]
