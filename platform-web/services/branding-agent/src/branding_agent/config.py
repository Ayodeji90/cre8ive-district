from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Path:
    """Find the repo-root .env without assuming a fixed directory depth.

    Works for both the source tree and an installed package inside a
    container, where no .env exists and settings come from the environment.
    """
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return Path.cwd() / ".env"


ENV_FILE = _find_env_file()


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
    LLM_ROUTING_ORDER: str = "openrouter"
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

    @model_validator(mode="after")
    def validate_production_guards(self) -> "Settings":
        if self.ENV == "production":
            if self.AI_STUB:
                raise ValueError("AI_STUB must be False in production.")
            if not self.SERVICE_API_KEY:
                raise ValueError("SERVICE_API_KEY is required in production.")
            has_llm_key = any(
                [
                    self.OPENROUTER_API_KEY,
                    self.ANTHROPIC_API_KEY,
                    self.OPENAI_API_KEY,
                    self.GROQ_API_KEY,
                    self.NVIDIA_NIM_API_KEY,
                ]
            )
            if not has_llm_key:
                raise ValueError("At least one LLM API key is required in production.")
        return self

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
