from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from run_engine.config import get_settings
from run_engine.domain.run import (
    ChannelPermissions,
    CreditBudget,
    Run,
    RunEvent,
    RunTask,
    TaskStatus,
)
from run_engine.events.publisher import InMemoryEventPublisher, RedisEventPublisher
from run_engine.logging import configure_logging, get_logger
from run_engine.orchestrator.briefer import format_brief_summary
from run_engine.orchestrator.executor import TaskExecutor
from run_engine.orchestrator.loop import AgentLoop, PlatformContextGatherer, SimpleContextGatherer
from run_engine.orchestrator.planner import TaskPlanner
from run_engine.persistence.repository import InMemoryRunRepository, PostgresRunRepository
from run_engine.providers.llm import create_planner_llm

configure_logging()
logger = get_logger("run_engine.api")


# --- Global singletons for runtime ---
settings = get_settings()
repository = (
    PostgresRunRepository(settings.DATABASE_URL)
    if not settings.USE_IN_MEMORY_REPO
    else InMemoryRunRepository()
)
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
event_publisher = (
    InMemoryEventPublisher() if settings.USE_IN_MEMORY_EVENTS else RedisEventPublisher(redis_client)
)
llm = create_planner_llm(settings)
planner = TaskPlanner(llm)
executor = TaskExecutor(llm=llm if not settings.AI_STUB else None)
loop_engine = AgentLoop(
    planner=planner,
    executor=executor,
    repository=repository,
    event_publisher=event_publisher,
    context_gatherer=SimpleContextGatherer()
    if settings.AI_STUB
    else PlatformContextGatherer(settings.PLATFORM_API_URL, settings.PLATFORM_API_KEY),
    iteration_delay=settings.ITERATION_DELAY_SECONDS,
    approval_timeout=settings.APPROVAL_TIMEOUT_SECONDS,
    brief_interval_hours=settings.BRIEF_INTERVAL_HOURS,
)


async def require_service_key(
    x_agent_key: str | None = Header(default=None, alias="X-Agent-Key"),
) -> None:
    if settings.ENV == "production" or settings.SERVICE_API_KEY:
        if not x_agent_key or x_agent_key != settings.SERVICE_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing service key",
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Abija Run Engine service")
    if hasattr(repository, "initialize"):
        await repository.initialize()
    if not settings.USE_IN_MEMORY_EVENTS:
        await redis_client.ping()
    active_runs = await repository.get_all_active_runs()
    recovered = loop_engine.recover_active_runs(active_runs)
    logger.info("Recovered %s persisted active runs", recovered)
    try:
        yield
    finally:
        await loop_engine.shutdown()
        await redis_client.aclose()
        if hasattr(repository, "close"):
            await repository.close()
    logger.info("Stopping Abija Run Engine service")


app = FastAPI(
    title="Abija Run Engine",
    description="Autonomous Agent Orchestrator for Cre8ive District",
    version="0.1.0",
    lifespan=lifespan,
)

cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---


class CreateRunRequest(BaseModel):
    business_id: UUID
    user_id: UUID
    credits_budget: int = 100
    goal: str = "Grow business presence, acquire customers, and improve conversion."
    permissions: ChannelPermissions = Field(default_factory=ChannelPermissions)
    max_iterations: int = 50


class TaskApprovalRequest(BaseModel):
    feedback: str | None = None


# --- Endpoints ---


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "planner_model": settings.PLANNER_MODEL,
        "stub_mode": settings.AI_STUB,
    }


@app.get("/ready")
async def ready_check():
    if not settings.USE_IN_MEMORY_REPO:
        try:
            from sqlalchemy import text

            async with repository._session_factory() as session:
                await session.execute(text("SELECT 1"))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database unreachable: {exc}",
            ) from exc
    return {"status": "ready", "service": settings.SERVICE_NAME}


@app.get("/v1/ping", dependencies=[Depends(require_service_key)])
async def ping():
    """Authenticated liveness probe: proves reachability and key agreement."""
    return {"status": "ok", "service": settings.SERVICE_NAME}


@app.post(
    "/v1/runs",
    status_code=status.HTTP_201_CREATED,
    response_model=Run,
    dependencies=[Depends(require_service_key)],
)
async def start_run(payload: CreateRunRequest):
    run = Run(
        business_id=payload.business_id,
        user_id=payload.user_id,
        budget=CreditBudget(total=payload.credits_budget, used=0),
        permissions=payload.permissions,
        goal=payload.goal,
        max_iterations=payload.max_iterations,
    )
    saved_run = await repository.create_run(run)
    loop_engine.spawn(saved_run)
    return saved_run


@app.get("/v1/runs/{run_id}", response_model=Run, dependencies=[Depends(require_service_key)])
async def get_run_status(run_id: UUID):
    run = await repository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.post("/v1/runs/{run_id}/pause", dependencies=[Depends(require_service_key)])
async def pause_run(run_id: UUID):
    run = await repository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    await loop_engine.pause(run)
    return {"status": "paused", "run_id": str(run_id)}


@app.post("/v1/runs/{run_id}/resume", dependencies=[Depends(require_service_key)])
async def resume_run(run_id: UUID):
    run = await repository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    await loop_engine.resume(run)
    return {"status": "resumed", "run_id": str(run_id)}


@app.post("/v1/runs/{run_id}/cancel", dependencies=[Depends(require_service_key)])
async def cancel_run(run_id: UUID):
    run = await repository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    await loop_engine.cancel(run)
    return {"status": "cancelled", "run_id": str(run_id)}


@app.get(
    "/v1/runs/{run_id}/tasks/pending",
    response_model=list[RunTask],
    dependencies=[Depends(require_service_key)],
)
async def get_pending_tasks(run_id: UUID):
    tasks = await repository.get_pending_approval_tasks(run_id)
    return tasks


@app.post("/v1/runs/{run_id}/tasks/{task_id}/approve", dependencies=[Depends(require_service_key)])
async def approve_task(run_id: UUID, task_id: UUID):
    task = await repository.get_task(task_id)
    if not task or task.run_id != run_id:
        raise HTTPException(status_code=404, detail="Task not found for this run")
    if task.status != TaskStatus.WAITING_APPROVAL:
        raise HTTPException(status_code=409, detail="Task is not waiting for approval")
    task.status = TaskStatus.APPROVED
    await repository.update_task(task)
    accepted = await loop_engine.approve_task(task_id, approved=True)
    return {
        "approved": True,
        "task_id": str(task_id),
        "unblocked": accepted or not loop_engine.is_running(run_id),
    }


@app.post("/v1/runs/{run_id}/tasks/{task_id}/reject", dependencies=[Depends(require_service_key)])
async def reject_task(run_id: UUID, task_id: UUID, body: TaskApprovalRequest | None = None):
    task = await repository.get_task(task_id)
    if not task or task.run_id != run_id:
        raise HTTPException(status_code=404, detail="Task not found for this run")
    if task.status != TaskStatus.WAITING_APPROVAL:
        raise HTTPException(status_code=409, detail="Task is not waiting for approval")
    task.status = TaskStatus.REJECTED
    await repository.update_task(task)
    accepted = await loop_engine.approve_task(task_id, approved=False)
    return {
        "approved": False,
        "task_id": str(task_id),
        "unblocked": accepted or not loop_engine.is_running(run_id),
    }


@app.get(
    "/v1/runs/{run_id}/events",
    response_model=list[RunEvent],
    dependencies=[Depends(require_service_key)],
)
async def list_events(run_id: UUID):
    events = await repository.get_events(run_id)
    return events


@app.get("/v1/runs/{run_id}/events/stream", dependencies=[Depends(require_service_key)])
async def stream_run_events(run_id: UUID):
    """Server-Sent Events (SSE) live event stream for a run."""
    run = await repository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_generator() -> AsyncIterator[str]:
        async for event in event_publisher.subscribe(run_id):
            payload = json.dumps(
                {
                    "id": str(event.id),
                    "run_id": str(event.run_id),
                    "event_type": event.event_type.value,
                    "message": event.message,
                    "task_id": str(event.task_id) if event.task_id else None,
                    "metadata": event.metadata,
                    "created_at": event.created_at.isoformat(),
                }
            )
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/v1/runs/{run_id}/brief", dependencies=[Depends(require_service_key)])
async def get_run_brief(run_id: UUID):
    run = await repository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return format_brief_summary(run)
