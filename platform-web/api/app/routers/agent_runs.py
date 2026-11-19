"""Authenticated platform facade for the internal run-engine service."""

import uuid
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import get_settings
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/agent/runs", tags=["agent-runs"])


class StartRunRequest(BaseModel):
    business_id: uuid.UUID
    goal: str = Field(min_length=8, max_length=1000)
    credits_budget: int | None = Field(default=None, ge=1, le=10000)
    max_iterations: int = Field(default=20, ge=1, le=100)


async def _assert_owner(db: AsyncSession, business_id: uuid.UUID, user_id: uuid.UUID) -> None:
    from app.models import Business

    business = await db.get(Business, business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.owner_id != user_id:
        raise HTTPException(status_code=403, detail="You do not own this business")


def _service_headers() -> dict[str, str]:
    settings = get_settings()
    if not settings.RUN_ENGINE_API_KEY:
        raise HTTPException(
            status_code=503, detail="Run engine service authentication is not configured"
        )
    return {"X-Agent-Key": settings.RUN_ENGINE_API_KEY}


async def _get_run(run_id: uuid.UUID) -> dict[str, Any]:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{settings.RUN_ENGINE_URL}/v1/runs/{run_id}", headers=_service_headers()
            )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Run not found")
        response.raise_for_status()
        return response.json()
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Run engine is unavailable") from exc


@router.post("", status_code=status.HTTP_201_CREATED)
async def start_run(
    payload: StartRunRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    await _assert_owner(db, payload.business_id, user.id)
    from app.models import Business

    business = await db.get(Business, payload.business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    budget = min(payload.credits_budget or business.credit_balance, business.credit_balance)
    if budget < 1:
        raise HTTPException(
            status_code=402, detail="No credits are available for an autonomous run"
        )
    settings = get_settings()
    body = payload.model_dump(mode="json")
    body.update(user_id=str(user.id), credits_budget=budget)
    body["permissions"] = {
        name: "ask_first"
        for name in (
            "website",
            "social_instagram",
            "social_facebook",
            "social_linkedin",
            "social_x",
            "social_tiktok",
            "outreach_email",
            "content",
        )
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{settings.RUN_ENGINE_URL}/v1/runs", json=body, headers=_service_headers()
            )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not start autonomous run") from exc


@router.get("/{run_id}")
async def run_status(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    run = await _get_run(run_id)
    await _assert_owner(db, uuid.UUID(run["business_id"]), user.id)
    if run.get("user_id") != str(user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this run")
    return run


@router.get("/{run_id}/events")
async def run_events(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    run = await _get_run(run_id)
    await _assert_owner(db, uuid.UUID(run["business_id"]), user.id)
    if run.get("user_id") != str(user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this run")
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{settings.RUN_ENGINE_URL}/v1/runs/{run_id}/events", headers=_service_headers()
            )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not load run events") from exc


@router.get("/{run_id}/events/stream")
async def stream_run_events(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    run = await _get_run(run_id)
    await _assert_owner(db, uuid.UUID(run["business_id"]), user.id)
    if run.get("user_id") != str(user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this run")
    settings = get_settings()

    async def relay():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "GET",
                f"{settings.RUN_ENGINE_URL}/v1/runs/{run_id}/events/stream",
                headers=_service_headers(),
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    yield chunk

    return StreamingResponse(
        relay(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _set_task_decision(
    run_id: uuid.UUID,
    task_id: uuid.UUID,
    decision: str,
    db: AsyncSession,
    user: User,
) -> dict[str, Any]:
    run = await _get_run(run_id)
    await _assert_owner(db, uuid.UUID(run["business_id"]), user.id)
    if run.get("user_id") != str(user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this run")
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{settings.RUN_ENGINE_URL}/v1/runs/{run_id}/tasks/{task_id}/{decision}",
                headers=_service_headers(),
            )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Pending task not found")
        if response.status_code == 409:
            raise HTTPException(status_code=409, detail="Task is no longer waiting for approval")
        response.raise_for_status()
        return response.json()
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not record task approval") from exc


@router.post("/{run_id}/tasks/{task_id}/approve")
async def approve_task(
    run_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return await _set_task_decision(run_id, task_id, "approve", db, user)


@router.post("/{run_id}/tasks/{task_id}/reject")
async def reject_task(
    run_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return await _set_task_decision(run_id, task_id, "reject", db, user)
