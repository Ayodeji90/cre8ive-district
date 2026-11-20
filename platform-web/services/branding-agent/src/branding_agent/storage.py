import asyncio
from typing import Protocol

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from branding_agent.config import Settings
from branding_agent.logging import get_logger

log = get_logger(__name__)


class StorageNotConfigured(RuntimeError):
    pass


class StorageError(RuntimeError):
    pass


class Storage(Protocol):
    async def upload_bytes(self, path: str, data: bytes, content_type: str) -> str: ...


class LocalStorage:
    async def upload_bytes(self, path: str, data: bytes, content_type: str) -> str:
        return f"local://{path}"


class R2Storage:
    def __init__(self, settings: Settings) -> None:
        self.bucket = settings.R2_BUCKET
        self.public_base = settings.R2_PUBLIC_URL.rstrip("/")
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY,
            aws_secret_access_key=settings.R2_SECRET_KEY,
            region_name="auto",
            config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
        )

    def public_url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.public_base}/{path}" if self.public_base else path

    async def upload_bytes(self, path: str, data: bytes, content_type: str) -> str:
        key = path.lstrip("/")

        def _put() -> None:
            self._client.put_object(
                Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
            )

        try:
            await asyncio.to_thread(_put)
        except (BotoCoreError, ClientError) as exc:
            log.exception("r2_upload_failed", path=key)
            raise StorageError(f"Upload failed for {key}") from exc
        return self.public_url(key)


def build_storage(settings: Settings) -> Storage:
    if not (settings.R2_ENDPOINT and settings.R2_ACCESS_KEY and settings.R2_SECRET_KEY):
        raise StorageNotConfigured("R2 object storage is not configured")
    return R2Storage(settings)


def storage_path(*parts: str) -> str:
    return "/".join(str(part).strip("/") for part in parts if part not in (None, ""))
