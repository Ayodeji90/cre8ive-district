"""Environment-backed application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cre8ive:localdev@localhost:5432/cre8ive"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Auth (tokens are issued by NextAuth on the frontend)
    JWT_SECRET: str = "dev-only-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    # Shared secret for NextAuth's server-to-server adapter calls. Falls back to
    # JWT_SECRET when unset.
    AUTH_ADAPTER_SECRET: str = ""

    # Branding Agent service
    BRANDING_AGENT_URL: str = "http://localhost:8001"
    BRANDING_AGENT_API_KEY: str = ""

    # Website Agent service
    WEBSITE_AGENT_URL: str = "http://localhost:8002"
    WEBSITE_AGENT_API_KEY: str = ""

    # Run Engine service
    RUN_ENGINE_URL: str = "http://localhost:8003"
    RUN_ENGINE_API_KEY: str = ""
    SERVICE_API_KEY: str = ""

    # Storage
    R2_ENDPOINT: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET: str = "cre8ive-assets"
    R2_PUBLIC_URL: str = ""

    # Payments
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"

    # Email
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Cre8ive District <brands@cre8ivedistrict.com>"

    # Vercel
    VERCEL_TOKEN: str = ""
    VERCEL_TEAM_ID: str = ""

    # WhatsApp (future)
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""

    # App
    MARKETING_URL: str = "http://localhost:3000"
    FRONTEND_URLS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002"
    ENV: str = "development"

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENV == "production":
            if not self.DATABASE_URL.startswith(("postgresql://", "postgresql+asyncpg://")):
                raise ValueError("DATABASE_URL must point to PostgreSQL in production.")
            if not self.SERVICE_API_KEY:
                raise ValueError("SERVICE_API_KEY is required in production.")
            if not self.WEBSITE_AGENT_API_KEY or not self.RUN_ENGINE_API_KEY or not self.BRANDING_AGENT_API_KEY:
                raise ValueError("Website, run-engine, and branding-agent service keys are required in production.")
            if not self.JWT_SECRET or self.JWT_SECRET == "dev-only-secret-change-me":
                raise ValueError("JWT_SECRET must be explicitly configured in production.")
        return self

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_URLS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
