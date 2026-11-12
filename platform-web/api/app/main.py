"""FastAPI application: middleware, lifespan, error handling, router mounting."""

import uuid
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import __version__
from app.config import get_settings
from app.deps import get_event_bus
from app.logging import configure_logging, get_logger
from app.routers import (
    assets,
    auth_adapter,
    billing,
    brands,
    businesses,
    chat,
    delivery,
    health,
    reviews,
    users,
    waitlist,
)

log = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.ENV)
    log.info("api_starting", version=__version__, env=settings.ENV)

    redis = None
    try:
        redis = aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        await redis.ping()
        app.state.redis = redis
        import app.deps as deps

        deps._redis = redis  # share the connection with the event bus
    except Exception:
        log.warning("redis_unavailable_at_startup", exc_info=True)
        app.state.redis = None

    try:
        from app.db import engine

        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        log.warning("database_unavailable_at_startup", exc_info=True)

    try:
        from app.llm.factory import get_ai_service

        app.state.ai = get_ai_service(settings)
    except Exception:
        log.warning("ai_service_unavailable", exc_info=True)
        app.state.ai = None

    get_event_bus()
    yield

    if redis is not None:
        await redis.aclose()
    log.info("api_stopped")


app = FastAPI(
    title="Cre8ive District API",
    version=__version__,
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)
    try:
        response = await call_next(request)
    finally:
        structlog.contextvars.clear_contextvars()
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(part) for part in error.get("loc", []) if part != "body"),
            "message": error.get("msg"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", path=request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(health.router)

api_router = APIRouter(prefix="/api")
api_router.include_router(users.router)
api_router.include_router(auth_adapter.router)
api_router.include_router(businesses.router)
api_router.include_router(brands.router)
api_router.include_router(chat.router)
api_router.include_router(billing.router)
api_router.include_router(billing.webhook_router)
api_router.include_router(reviews.internal_router)
api_router.include_router(reviews.admin_router)
api_router.include_router(assets.router)
api_router.include_router(delivery.router)
api_router.include_router(waitlist.router)
app.include_router(api_router)
