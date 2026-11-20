"""Ideogram 3 image generation provider."""

import uuid

import httpx

from branding_agent.logging import get_logger
from branding_agent.storage import Storage, storage_path

from .base import ImageResult

log = get_logger(__name__)

IDEOGRAM_API = "https://api.ideogram.ai/generate"
COST_PER_IMAGE = 0.08
MAX_RETRIES = 2


class IdeogramProvider:
    def __init__(self, api_key: str, storage: Storage) -> None:
        self._api_key = api_key
        self._storage = storage

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str | None = None,
        n: int = 1,
    ) -> list[ImageResult]:
        w, h = (int(d) for d in size.split("x"))
        payload: dict = {
            "image_request": {
                "prompt": prompt,
                "model": "V_3",
                "magic_prompt_option": "AUTO",
                "aspect_ratio": "ASPECT_1_1" if w == h else "ASPECT_16_9",
                "num_images": n,
            }
        }
        if style:
            payload["image_request"]["style_type"] = style

        headers = {"Api-Key": self._api_key, "Content-Type": "application/json"}

        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    resp = await client.post(IDEOGRAM_API, json=payload, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                break
            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc
                log.warning("ideogram_retry", attempt=attempt + 1)
                if attempt < MAX_RETRIES - 1:
                    import asyncio

                    await asyncio.sleep(1.0 * (2**attempt))
        else:
            raise RuntimeError("Ideogram API failed after retries") from last_exc

        results: list[ImageResult] = []
        for img in data.get("data", []):
            image_url = img.get("url", "")
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
                    provider="ideogram",
                    cost_usd=COST_PER_IMAGE,
                )
            )

        log.info("image_gen", provider="ideogram", count=len(results), cost_usd=COST_PER_IMAGE * n)
        return results
