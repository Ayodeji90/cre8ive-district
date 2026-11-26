from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "website-agent"
    AGENT_KEY: str = ""
    SERVICE_API_KEY: str = ""
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    ENV: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./website_agent.db"
    USE_IN_MEMORY_REPO: bool = True

    # LLM Settings
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"
    WEBSITE_MODEL: str = "anthropic/claude-sonnet-4"
    AI_STUB: bool = True

    # Vercel Deployment Settings
    VERCEL_TOKEN: str = ""
    VERCEL_TEAM_ID: str | None = None
    VERCEL_SCOPE: str | None = None
    PRIMARY_DOMAIN_SUFFIX: str = "cre8ivedistrict.app"  # e.g., slug.cre8ivedistrict.app
    DEPLOY_STUB: bool = True  # True: return mock Vercel deployment URL

    @model_validator(mode="after")
    def validate_production_guards(self) -> "Settings":
        if self.ENV == "production":
            if self.AI_STUB:
                raise ValueError("AI_STUB must be False in production.")
            if self.DEPLOY_STUB:
                raise ValueError("DEPLOY_STUB must be False in production.")
            if not self.VERCEL_TOKEN:
                raise ValueError("VERCEL_TOKEN is required in production.")
            if self.USE_IN_MEMORY_REPO:
                raise ValueError(
                    "USE_IN_MEMORY_REPO must be False in production (PostgreSQL required)."
                )
            if not self.SERVICE_API_KEY:
                raise ValueError("SERVICE_API_KEY is required in production.")
            if not self.DATABASE_URL.startswith(("postgresql://", "postgresql+asyncpg://")):
                raise ValueError("DATABASE_URL must point to PostgreSQL in production.")
            if not self.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY is required in production.")
        return self

    model_config = {
        "env_file": "../../../.env",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
