import pytest

from app.config import Settings
from app.services.storage import LocalStorage, StorageNotConfigured, build_storage


@pytest.mark.asyncio
async def test_unconfigured_development_storage_uses_local_stub():
    storage = build_storage(
        Settings(
            ENV="development",
            R2_ENDPOINT="",
            R2_ACCESS_KEY="",
            R2_SECRET_KEY="",
        )
    )

    assert isinstance(storage, LocalStorage)
    assert await storage.upload_bytes("assets/kit.zip", b"asset", "application/zip") == (
        "local://assets/kit.zip"
    )
    assert await storage.presigned_url("assets/kit.zip") == "local://assets/kit.zip"
    await storage.delete("assets/kit.zip")


def test_unconfigured_production_storage_still_fails():
    settings = Settings(
        ENV="production",
        JWT_SECRET="production-secret",
        SERVICE_API_KEY="service-key",
        BRANDING_AGENT_API_KEY="branding-key",
        WEBSITE_AGENT_API_KEY="website-key",
        RUN_ENGINE_API_KEY="run-engine-key",
        R2_ENDPOINT="",
        R2_ACCESS_KEY="",
        R2_SECRET_KEY="",
    )

    with pytest.raises(StorageNotConfigured, match="R2 object storage is not configured"):
        build_storage(settings)
