"""Redis pub/sub event bus with an in-process fallback for local dev and tests."""

import asyncio
import contextlib
import json
from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as aioredis

from app.logging import get_logger

log = get_logger(__name__)

ADMIN_EVENTS_CHANNEL = "admin:events"


class EventBus:
    """Publishes events to Redis and streams them to SSE subscribers."""

    def __init__(self, redis: aioredis.Redis | None = None) -> None:
        self._redis = redis
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._lock = asyncio.Lock()

    async def publish(self, event: str, data: dict[str, Any]) -> None:
        payload = {"event": event, "data": data}
        if self._redis is not None:
            try:
                await self._redis.publish(ADMIN_EVENTS_CHANNEL, json.dumps(payload))
                return
            except Exception:  # pragma: no cover - redis outage fallback
                log.warning("redis_publish_failed", event_name=event, exc_info=True)
        async with self._lock:
            for queue in list(self._subscribers):
                queue.put_nowait(payload)

    async def subscribe(self) -> AsyncGenerator[dict[str, Any], None]:
        """Yields events. Uses Redis when available, otherwise a local queue."""
        if self._redis is not None:
            pubsub = self._redis.pubsub()
            await pubsub.subscribe(ADMIN_EVENTS_CHANNEL)
            try:
                async for message in pubsub.listen():
                    if message.get("type") != "message":
                        continue
                    yield json.loads(message["data"])
                return
            except Exception:  # pragma: no cover - redis outage fallback
                log.warning("redis_subscribe_failed", exc_info=True)
            finally:
                with contextlib.suppress(Exception):
                    await pubsub.unsubscribe(ADMIN_EVENTS_CHANNEL)
                    await pubsub.aclose()

        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        async with self._lock:
            self._subscribers.add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            async with self._lock:
                self._subscribers.discard(queue)
