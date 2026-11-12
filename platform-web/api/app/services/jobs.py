"""Background job enqueueing (arq / Redis)."""

import uuid

from app.config import get_settings
from app.logging import get_logger

log = get_logger(__name__)


async def enqueue_brand_generation(business_id: uuid.UUID) -> bool:
    """Queue the brand pipeline; never fails the caller if the queue is down."""
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        redis = await create_pool(RedisSettings.from_dsn(get_settings().REDIS_URL))
        try:
            await redis.enqueue_job("generate_brand_job", str(business_id))
        finally:
            await redis.aclose()
        return True
    except Exception:
        log.warning(
            "brand_generation_enqueue_failed",
            business_id=str(business_id),
            exc_info=True,
        )
        return False


async def enqueue_asset_render(brand_id: uuid.UUID) -> bool:
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        redis = await create_pool(RedisSettings.from_dsn(get_settings().REDIS_URL))
        try:
            await redis.enqueue_job("render_assets_job", str(brand_id))
        finally:
            await redis.aclose()
        return True
    except Exception:
        log.warning("asset_render_enqueue_failed", brand_id=str(brand_id), exc_info=True)
        return False
