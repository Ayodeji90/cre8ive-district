"""Environment-backed application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_URLS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
