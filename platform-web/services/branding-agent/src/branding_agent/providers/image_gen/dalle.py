"""DALL-E 3 image generation provider."""

import uuid

import httpx
import openai

from branding_agent.logging import get_logger
from branding_agent.storage import Storage, storage_path

from .base import ImageResult

log = get_logger(__name__)

COST_PER_IMAGE = 0.04
MAX_RETRIES = 2


class DalleProvider:
    def __init__(self, api_key: str, storage: Storage) -> None:
        self._client = openai.AsyncOpenAI(api_key=api_key)
        self._storage = storage

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str | None = None,
        n: int = 1,
    ) -> list[ImageResult]:
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await self._client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    quality="standard",
                    n=1,  # DALL-E 3 only supports n=1 per call
                )
                break
            except (openai.RateLimitError, openai.APIConnectionError) as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    import asyncio

                    await asyncio.sleep(1.0 * (2**attempt))
        else:
            raise RuntimeError("DALL-E API failed after retries") from last_exc

        results: list[ImageResult] = []
        for img_data in response.data:
            image_url = img_data.url
            if not image_url:
                continue

            async with httpx.AsyncClient(timeout=60) as client:
                img_resp = await client.get(image_url)
                img_resp.raise_for_status()
                img_bytes = img_resp.content

            r2_path = storage_path("logos", f"{uuid.uuid4().hex}.png")
            public_url = await self._storage.upload_bytes(r2_path, img_bytes, "image/png")

            results.append(
                ImageResult(
                    url=public_url,
                    prompt_used=prompt,
                    provider="dalle",
                    cost_usd=COST_PER_IMAGE,
                )
            )

        # DALL-E 3 only does n=1 per call; loop for multiple images
        for _ in range(n - 1):
            extra = await self.generate(prompt, size, style, n=1)
            results.extend(extra)

        log.info("image_gen", provider="dalle", count=len(results), cost_usd=COST_PER_IMAGE * n)
        return results
