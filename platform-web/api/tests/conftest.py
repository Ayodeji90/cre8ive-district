import os
import uuid

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["ENV"] = "test"
os.environ["FRONTEND_URLS"] = "http://localhost:3000"
os.environ["PAYSTACK_SECRET_KEY"] = "sk_test_webhook"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.config import get_settings
from app.db import Base, get_db
from app.deps import get_ai
from app.main import app
from app.models import User
from app.schemas.ai import (
    BrandCopy,
    BrandStrategy,
    ColorPalette,
    FontPair,
    FontSpec,
    PaletteResult,
    ValidationResult,
)


class FakeAIService:
    async def respond(self, context, history, message):
        yield "Hello from Abija."

    async def extract_context(self, history):
        user_messages = sum(message["role"] == "user" for message in history)
        return {
            "conversation_stage": (
                "summary_confirm" if user_messages >= 7 else "business_description"
            ),
            "ready_to_generate": user_messages >= 8,
        }

    async def generate_strategy(self, description, industry, preferences):
        name = preferences.get("business_name") or "Test Brand"
        return BrandStrategy(
            primary_name=name,
            positioning=f"A distinctive {industry} brand for {description}",
            tagline="Made for what's next",
            brand_story=f"{name} began with a clear idea and a community to serve.",
            elevator_pitch=f"{name} serves its community through {description}.",
            target_description="Local customers",
        )

    async def generate_logos(self, strategy, industry, style_keywords=None):
        return [f"https://assets.test/{strategy.primary_name}-{i}.png" for i in range(3)]

    async def derive_palette(self, strategy, industry):
        return PaletteResult(
            palette=ColorPalette(
                primary="#123456",
                secondary="#345678",
                accent="#567890",
                neutral="#111111",
                background="#FFFFFF",
            ),
            contrast_scores={},
            passes_wcag_aa=True,
        )

    async def select_fonts(self, strategy):
        return FontPair(
            heading=FontSpec(family="Inter", weight=700),
            body=FontSpec(family="Inter", weight=400),
        )

    async def generate_copy(self, strategy):
        return BrandCopy(tagline_variants=[strategy.tagline])

    async def validate_output(self, strategy, palette, fonts, logo_urls):
        return ValidationResult(passed=True)


class FakeStorage:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    def public_url(self, path: str) -> str:
        return f"https://assets.test/{path.lstrip('/')}"

    async def upload_bytes(self, path: str, data: bytes, content_type: str) -> str:
        self.files[path.lstrip("/")] = data
        return self.public_url(path)

    async def presigned_url(self, path: str, expires_in: int = 7 * 24 * 3600) -> str:
        return f"https://signed.test/{path.lstrip('/')}?expires={expires_in}"

    async def delete(self, path: str) -> None:
        self.files.pop(path.lstrip("/"), None)


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ai] = FakeAIService
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def storage():
    return FakeStorage()


@pytest_asyncio.fixture
async def customer(session_factory):
    user = User(id=uuid.uuid4(), email="customer@example.com", name="Customer", role="customer")
    async with session_factory() as db:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin(session_factory):
    user = User(id=uuid.uuid4(), email="designer@example.com", name="Designer", role="designer")
    async with session_factory() as db:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


def auth_headers(user: User) -> dict[str, str]:
    token = jwt.encode(
        {"sub": str(user.id), "email": user.email, "role": user.role},
        get_settings().JWT_SECRET,
        algorithm=get_settings().JWT_ALGORITHM,
    )
    return {"Authorization": f"Bearer {token}"}
