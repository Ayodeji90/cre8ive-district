"""Cloudflare R2 (S3-compatible) object storage."""

import asyncio
from typing import Protocol

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.config import Settings
from app.logging import get_logger

log = get_logger(__name__)


class StorageNotConfigured(RuntimeError):
    pass


class StorageError(RuntimeError):
    pass


class Storage(Protocol):
    async def upload_bytes(self, path: str, data: bytes, content_type: str) -> str:
        """Upload bytes and return the public URL for `path`."""
        ...

    async def presigned_url(self, path: str, expires_in: int = 7 * 24 * 3600) -> str: ...

    async def delete(self, path: str) -> None: ...

    def public_url(self, path: str) -> str: ...


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
        if self.public_base:
            return f"{self.public_base}/{path}"
        return path

    async def upload_bytes(self, path: str, data: bytes, content_type: str) -> str:
        path = path.lstrip("/")

        def _put() -> None:
            self._client.put_object(
                Bucket=self.bucket, Key=path, Body=data, ContentType=content_type
            )

        try:
            await asyncio.to_thread(_put)
        except (BotoCoreError, ClientError) as exc:
            log.error("r2_upload_failed", path=path, exc_info=True)
            raise StorageError(f"Upload failed for {path}") from exc
        return self.public_url(path)

    async def presigned_url(self, path: str, expires_in: int = 7 * 24 * 3600) -> str:
        path = path.lstrip("/")

        def _sign() -> str:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": path},
                ExpiresIn=expires_in,
            )

        try:
            return await asyncio.to_thread(_sign)
        except (BotoCoreError, ClientError) as exc:
            raise StorageError(f"Could not sign {path}") from exc

    async def delete(self, path: str) -> None:
        path = path.lstrip("/")

        def _delete() -> None:
            self._client.delete_object(Bucket=self.bucket, Key=path)

        await asyncio.to_thread(_delete)


def build_storage(settings: Settings) -> Storage:
    if not (settings.R2_ENDPOINT and settings.R2_ACCESS_KEY and settings.R2_SECRET_KEY):
        raise StorageNotConfigured
    return R2Storage(settings)


def storage_path(*parts: str) -> str:
    """Build an R2 key from non-empty parts."""
    return "/".join(str(part).strip("/") for part in parts if part not in (None, ""))
