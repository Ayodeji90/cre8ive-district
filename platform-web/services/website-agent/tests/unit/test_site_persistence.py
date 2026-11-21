from uuid import uuid4

import pytest

from website_agent.persistence.repository import SiteJobRepository


@pytest.mark.asyncio
async def test_site_persistence_lifecycle():
    repo = SiteJobRepository("sqlite+aiosqlite:///:memory:")
    await repo.initialize()

    site_id = uuid4()
    business_id = uuid4()
    spec = {"site_id": str(site_id), "theme": "clean"}
    files = {"index.html": "<html><body>Hello Lagos</body></html>"}
    quality = {"passed": True, "score": 98}

    # Save
    job = await repo.save_site(site_id, business_id, spec, files, quality)
    assert job.id == site_id
    assert job.status == "generated"
    assert job.files_json["index.html"] == "<html><body>Hello Lagos</body></html>"

    # Get
    fetched = await repo.get_site(site_id)
    assert fetched is not None
    assert fetched.id == site_id
    assert fetched.business_id == business_id
    assert fetched.status == "generated"

    # Update deployment
    deployment = {"live_url": "https://test.cre8ive.ng", "ready_state": "READY"}
    await repo.update_deployment(site_id, deployment)

    fetched_after_deploy = await repo.get_site(site_id)
    assert fetched_after_deploy.status == "deployed"
    assert fetched_after_deploy.deployment_json["live_url"] == "https://test.cre8ive.ng"
