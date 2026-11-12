"""Paystack HTTP client and webhook signature verification."""

import hashlib
import hmac

import httpx

from app.logging import get_logger

log = get_logger(__name__)

PLAN_AMOUNTS: dict[str, float] = {
    "brand_starter": 20000.00,
    "brand_web": 60000.00,
    "brand_complete": 120000.00,
    "designer_review": 25000.00,
}


class PaystackError(RuntimeError):
    pass


class PaystackClient:
    def __init__(self, secret_key: str, base_url: str = "https://api.paystack.co") -> None:
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.secret_key}", "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=20.0) as client:
            try:
                response = await client.request(method, path, headers=self.headers, **kwargs)
            except httpx.HTTPError as exc:
                raise PaystackError("Could not reach Paystack") from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise PaystackError("Invalid response from Paystack") from exc
        if response.status_code >= 400 or not payload.get("status", False):
            log.error("paystack_error", path=path, status=response.status_code, payload=payload)
            raise PaystackError(payload.get("message", "Paystack request failed"))
        return payload["data"]

    async def initialize_transaction(
        self,
        *,
        email: str,
        amount_naira: float,
        reference: str,
        callback_url: str,
        metadata: dict,
    ) -> dict:
        return await self._request(
            "POST",
            "/transaction/initialize",
            json={
                "email": email,
                "amount": int(round(amount_naira * 100)),  # kobo
                "reference": reference,
                "callback_url": callback_url,
                "metadata": metadata,
            },
        )

    async def verify_transaction(self, reference: str) -> dict:
        return await self._request("GET", f"/transaction/verify/{reference}")


def verify_webhook_signature(body: bytes, signature: str | None, secret_key: str) -> bool:
    if not signature or not secret_key:
        return False
    expected = hmac.new(secret_key.encode(), body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature)
