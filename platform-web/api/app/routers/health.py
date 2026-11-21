"""Liveness and dependency-readiness endpoints."""

import asyncio
import time
from typing import Any

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.config import get_settings
from app.db import get_db

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": __version__}


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)) -> dict:
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


async def _check_database() -> dict[str, Any]:
    from app.db import engine

    started = time.perf_counter()
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {"status": "ok", "latency_ms": round((time.perf_counter() - started) * 1000, 1)}
    except Exception as exc:  # diagnostics must report, not raise
        return {"status": "error", "error": str(exc)}


async def _check_redis() -> dict[str, Any]:
    started = time.perf_counter()
    client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        await client.ping()
        return {"status": "ok", "latency_ms": round((time.perf_counter() - started) * 1000, 1)}
    except Exception as exc:  # diagnostics must report, not raise
        return {"status": "error", "error": str(exc)}
    finally:
        await client.aclose()


async def _check_http(
    client: httpx.AsyncClient, name: str, base_url: str, api_key: str
) -> dict[str, Any]:
    started = time.perf_counter()
    url = f"{base_url.rstrip('/')}/v1/ping"
    try:
        response = await client.get(url, headers={"X-Agent-Key": api_key})
        body: Any
        try:
            body = response.json()
        except ValueError:
            body = response.text[:200]
        ok = response.is_success
        result: dict[str, Any] = {
            "status": "ok" if ok else "error",
            "http_status": response.status_code,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "service": name,
        }
        if not ok:
            result["body"] = body
        return result
    except Exception as exc:  # diagnostics must report, not raise
        return {
            "status": "error",
            "service": name,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "error": str(exc),
        }


@router.get("/health/deps")
async def health_deps(response: Response) -> dict[str, Any]:
    """Check every dependency chat and generation need, in parallel.

    Returns 503 when any dependency is unhealthy so this can be used as a
    deploy smoke test. Each dependency reports independently for diagnosis.
    """
    async with httpx.AsyncClient(timeout=2.0) as client:
        results = await asyncio.gather(
            _check_database(),
            _check_redis(),
            _check_http(
                client,
                "branding-agent",
                settings.BRANDING_AGENT_URL,
                settings.BRANDING_AGENT_API_KEY,
            ),
            _check_http(
                client, "website-agent", settings.WEBSITE_AGENT_URL, settings.WEBSITE_AGENT_API_KEY
            ),
            _check_http(client, "run-engine", settings.RUN_ENGINE_URL, settings.RUN_ENGINE_API_KEY),
        )

    names = ["database", "redis", "branding-agent", "website-agent", "run-engine"]
    dependencies = dict(zip(names, results, strict=True))
    healthy = all(item["status"] == "ok" for item in dependencies.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ok" if healthy else "degraded",
        "version": __version__,
        "dependencies": dependencies,
    }
