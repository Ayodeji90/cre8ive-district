from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-5-5"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = ""
    NVIDIA_NIM_API_KEY: str = ""
    NVIDIA_NIM_MODEL: str = ""
    NVIDIA_NIM_API_BASE: str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = ""
    OPENROUTER_API_BASE: str = ""
    IDEOGRAM_API_KEY: str = ""
    LLM_PROVIDER: str = ""
    LLM_ROUTING_ORDER: str = "groq,nvidia_nim,openrouter,anthropic,openai"
    LLM_PROVIDER_TIMEOUT_SECONDS: float = Field(default=20, gt=0, le=120)
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
