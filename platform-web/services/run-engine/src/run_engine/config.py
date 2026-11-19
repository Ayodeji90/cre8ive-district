from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "run-engine"
    AGENT_KEY: str = ""
    SERVICE_API_KEY: str = ""
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    ENV: str = "development"

    # Database & Redis
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_IN_MEMORY_REPO: bool = True
    USE_IN_MEMORY_EVENTS: bool = True

    # LLM for task planning
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"
    PLANNER_MODEL: str = "anthropic/claude-sonnet-4"
    PLANNER_TEMPERATURE: float = 0.3
    PLANNER_MAX_TOKENS: int = 4096
    AI_STUB: bool = True

    # Agent Loop parameters
    ITERATION_DELAY_SECONDS: float = 1.0
    MAX_ITERATIONS_PER_RUN: int = 100
    APPROVAL_TIMEOUT_SECONDS: float = 86400.0  # 24 hours
    BRIEF_INTERVAL_HOURS: float = 6.0

    # Service endpoints
    BRANDING_AGENT_URL: str = "http://localhost:8001"
    WEBSITE_AGENT_URL: str = "http://localhost:8003"
    PLATFORM_API_URL: str = "http://localhost:8000"
    PLATFORM_API_KEY: str = ""

    @model_validator(mode="after")
    def validate_production_guards(self) -> "Settings":
        if self.ENV == "production":
            if self.AI_STUB:
                raise ValueError("AI_STUB must be False in production.")
            if not self.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY is required in production.")
            if self.USE_IN_MEMORY_REPO:
                raise ValueError(
                    "USE_IN_MEMORY_REPO must be False in production (PostgreSQL required)."
                )
            if self.USE_IN_MEMORY_EVENTS:
                raise ValueError(
                    "USE_IN_MEMORY_EVENTS must be False in production (Redis pub/sub required)."
                )
            if not self.DATABASE_URL.startswith(("postgresql://", "postgresql+asyncpg://")):
                raise ValueError("DATABASE_URL must point to PostgreSQL in production.")
            if not self.SERVICE_API_KEY:
                raise ValueError("SERVICE_API_KEY is required in production.")
            if not self.PLATFORM_API_KEY:
                raise ValueError("PLATFORM_API_KEY is required in production.")
        return self

    model_config = {
        "env_file": "../../../.env",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
