from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, Protocol
from uuid import UUID

import redis.asyncio as aioredis
from run_engine.domain.run import RunEvent


class EventPublisher(Protocol):
    async def publish(self, event: RunEvent) -> None: ...
    async def subscribe(self, run_id: UUID) -> AsyncIterator[RunEvent]: ...


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self._subscribers: dict[UUID, list[asyncio.Queue[RunEvent]]] = {}
        self._lock = asyncio.Lock()

    async def publish(self, event: RunEvent) -> None:
        async with self._lock:
            queues = self._subscribers.get(event.run_id, [])
            for q in queues:
                await q.put(event)

    async def subscribe(self, run_id: UUID) -> AsyncIterator[RunEvent]:
        queue: asyncio.Queue[RunEvent] = asyncio.Queue()
        async with self._lock:
            if run_id not in self._subscribers:
                self._subscribers[run_id] = []
            self._subscribers[run_id].append(queue)
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            async with self._lock:
                if run_id in self._subscribers and queue in self._subscribers[run_id]:
                    self._subscribers[run_id].remove(queue)


class RedisEventPublisher:
    """Cross-process event fanout for SSE clients and run workers."""
    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    async def publish(self, event: RunEvent) -> None:
        await self._redis.publish(f"run-events:{event.run_id}", event.model_dump_json())

    async def subscribe(self, run_id: UUID) -> AsyncIterator[RunEvent]:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(f"run-events:{run_id}")
        try:
            async for message in pubsub.listen():
                if message.get("type") == "message":
                    yield RunEvent.model_validate_json(message["data"])
        finally:
            await pubsub.unsubscribe(f"run-events:{run_id}")
            await pubsub.aclose()
