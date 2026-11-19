"""FastAPI application: middleware, lifespan, error handling, router mounting."""

import json
import uuid
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import __version__
from app.config import get_settings
from app.deps import get_event_bus
from app.logging import configure_logging, get_logger
from app.routers import (
    agent_runs,
    assets,
    auth_adapter,
    billing,
    brands,
    businesses,
    chat,
    delivery,
    health,
    projects,
    reviews,
    users,
    waitlist,
    websites,
)

log = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.ENV)
    log.info("api_starting", version=__version__, env=settings.ENV)

    redis = None
    try:
        redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
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
api_router.include_router(agent_runs.router)
api_router.include_router(delivery.router)
api_router.include_router(projects.router)
api_router.include_router(waitlist.router)
api_router.include_router(websites.router)


@api_router.get("/internal/businesses/{business_id}/agent-context")
async def agent_business_context(
    business_id: uuid.UUID,
    x_agent_key: str | None = Header(default=None, alias="X-Agent-Key"),
):
    if not settings.SERVICE_API_KEY or x_agent_key != settings.SERVICE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing service key")
    from sqlalchemy import func, select

    from app.db import async_session_factory
    from app.models import Brand, Business, Order, Website

    async with async_session_factory() as db:
        business = await db.get(Business, business_id)
        if business is None:
            raise HTTPException(status_code=404, detail="Business not found")
        brand = (
            (
                await db.execute(
                    select(Brand)
                    .where(Brand.business_id == business_id)
                    .order_by(Brand.created_at.desc())
                )
            )
            .scalars()
            .first()
        )
        website = (
            (
                await db.execute(
                    select(Website)
                    .where(Website.business_id == business_id)
                    .order_by(Website.created_at.desc())
                )
            )
            .scalars()
            .first()
        )
        paid_order_stats = await db.execute(
            select(func.count(Order.id), func.coalesce(func.sum(Order.amount), 0)).where(
                Order.business_id == business_id, Order.status == "paid"
            )
        )
        total_orders, total_revenue = paid_order_stats.one()
        brand_summary = ""
        if brand:
            brand_summary = json.dumps(
                {"strategy": brand.strategy, "colors": brand.colors, "fonts": brand.fonts},
                ensure_ascii=False,
            )
        return {
            "business_id": str(business.id),
            "business_name": business.name,
            "business_description": business.description or "",
            "industry": business.industry or "",
            "target_audience": (business.preferences or {}).get("target_audience", ""),
            "has_brand": bool(brand and brand.status != "failed"),
            "brand_summary": brand_summary,
            "has_website": bool(website and website.status == "deployed"),
            "website_url": website.deployment_url or "" if website else "",
            "website_page_count": len(website.pages or []) if website else 0,
            "total_revenue": float(total_revenue),
            "total_orders": total_orders,
            "known_competitors": [],
        }


app.include_router(api_router)
