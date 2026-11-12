from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    IDEOGRAM_API_KEY: str = ""
    LLM_PROVIDER: str = "anthropic"
    IMAGE_PROVIDER: str = "ideogram"
    AI_STUB: bool = False
    SERVICE_API_KEY: str = ""

    R2_ENDPOINT: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET: str = "cre8ive-assets"
    R2_PUBLIC_URL: str = ""
    ENV: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
