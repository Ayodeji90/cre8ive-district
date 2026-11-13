"""Image generation protocol."""

from typing import Protocol

from pydantic import BaseModel


class ImageResult(BaseModel):
    url: str
    prompt_used: str
    provider: str
    cost_usd: float


class ImageProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str | None = None,
        n: int = 1,
    ) -> list[ImageResult]: ...
