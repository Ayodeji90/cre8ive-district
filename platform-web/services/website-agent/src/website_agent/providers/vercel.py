from __future__ import annotations

import asyncio
import base64
import logging
import uuid
from datetime import UTC, datetime
from typing import Protocol

import httpx

from website_agent.config import Settings
from website_agent.domain.spec import DeploymentResult, SiteSpec

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(UTC)


class VercelDeployer(Protocol):
    async def deploy(self, site: SiteSpec, file_tree: dict[str, str]) -> DeploymentResult: ...


class MockVercelDeployer:
    """Mock deployer for testing and local development without a live Vercel token."""

    def __init__(self, domain_suffix: str = "cre8ive.ng") -> None:
        self._domain_suffix = domain_suffix

    async def deploy(self, site: SiteSpec, file_tree: dict[str, str]) -> DeploymentResult:
        subdomain = site.subdomain or f"site-{uuid.uuid4().hex[:8]}"
        project_id = f"prj_{uuid.uuid4().hex[:12]}"
        deployment_id = f"dpl_{uuid.uuid4().hex[:16]}"
        live_url = f"https://{subdomain}.{self._domain_suffix}"

        logger.info(
            "Mock deployed site '%s' (%d files) to %s",
            site.brand.name,
            len(file_tree),
            live_url,
        )

        return DeploymentResult(
            site_id=site.site_id,
            project_id=project_id,
            deployment_id=deployment_id,
            live_url=live_url,
            subdomain=subdomain,
            files_count=len(file_tree),
            deployed_at=utc_now(),
            ready_state="READY",
        )


class LiveVercelDeployer:
    """Production deployer calling Vercel REST API v13 to create projects and publish static sites."""

    def __init__(self, settings: Settings) -> None:
        self._token = settings.VERCEL_TOKEN
        self._team_id = settings.VERCEL_TEAM_ID
        self._domain_suffix = settings.PRIMARY_DOMAIN_SUFFIX
        self._base_url = "https://api.vercel.com"

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    @property
    def _params(self) -> dict[str, str]:
        return {"teamId": self._team_id} if self._team_id else {}

    async def deploy(self, site: SiteSpec, file_tree: dict[str, str]) -> DeploymentResult:
        subdomain = site.subdomain or f"site-{uuid.uuid4().hex[:8]}"
        project_name = f"cd-{subdomain}"

        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # 1. Ensure project exists
                    project_id = await self._ensure_project(client, project_name)

                    # 2. Upload file tree to Vercel v13 deployments
                    deployment_payload_files = [
                        {
                            "file": filename,
                            "data": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
                            "encoding": "base64",
                        }
                        for filename, content in file_tree.items()
                    ]

                    deploy_res = await client.post(
                        f"{self._base_url}/v13/deployments",
                        headers=self._headers,
                        params=self._params,
                        json={
                            "name": project_name,
                            "target": "production",
                            "files": deployment_payload_files,
                            "projectSettings": {
                                "framework": None,
                                "outputDirectory": ".",
                            },
                        },
                    )
                    deploy_res.raise_for_status()
                    deploy_data = deploy_res.json()
                    deployment_id = deploy_data["id"]

                    # Vercel accepts deployments asynchronously; do not publish a URL before READY.
                    state = deploy_data.get("readyState", "BUILDING")
                    for _ in range(30):
                        if state in {"READY", "ERROR", "CANCELED"}:
                            break
                        await asyncio.sleep(2)
                        status_res = await client.get(
                            f"{self._base_url}/v13/deployments/{deployment_id}",
                            headers=self._headers,
                            params=self._params,
                        )
                        status_res.raise_for_status()
                        deploy_data = status_res.json()
                        state = deploy_data.get("readyState", state)
                    if state != "READY":
                        raise RuntimeError(f"Vercel deployment finished in state {state}")

                    # 3. Assign custom subdomain (e.g. slug.cre8ive.ng)
                    custom_domain = f"{subdomain}.{self._domain_suffix}"
                    await self._assign_domain(client, project_id, custom_domain)

                    live_url = f"https://{custom_domain}"
                    return DeploymentResult(
                        site_id=site.site_id,
                        project_id=project_id,
                        deployment_id=deployment_id,
                        live_url=live_url,
                        subdomain=subdomain,
                        files_count=len(file_tree),
                        deployed_at=utc_now(),
                        ready_state="READY",
                    )
            except (
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.HTTPStatusError,
                RuntimeError,
            ) as exc:
                last_error = exc
                logger.warning("Vercel deployment attempt %d failed: %s", attempt, exc)
                if attempt < 3:
                    await asyncio.sleep(attempt * 2.0)

        raise RuntimeError(f"Vercel deployment failed after 3 attempts: {last_error}")

    async def _ensure_project(self, client: httpx.AsyncClient, name: str) -> str:
        res = await client.get(
            f"{self._base_url}/v9/projects/{name}",
            headers=self._headers,
            params=self._params,
        )
        if res.status_code == 200:
            return res.json()["id"]

        create_res = await client.post(
            f"{self._base_url}/v10/projects",
            headers=self._headers,
            params=self._params,
            json={
                "name": name,
                "framework": None,
                "outputDirectory": ".",
                "publicSource": False,
            },
        )
        create_res.raise_for_status()
        return create_res.json()["id"]

    async def _assign_domain(self, client: httpx.AsyncClient, project_id: str, domain: str) -> None:
        try:
            existing = await client.get(
                f"{self._base_url}/v9/projects/{project_id}/domains/{domain}",
                headers=self._headers,
                params=self._params,
            )
            if existing.status_code == 200:
                return
            response = await client.post(
                f"{self._base_url}/v10/projects/{project_id}/domains",
                headers=self._headers,
                params=self._params,
                json={"name": domain},
            )
            response.raise_for_status()
        except Exception as exc:
            logger.error("Could not assign domain %s: %s", domain, exc)
            raise


def create_vercel_deployer(settings: Settings) -> VercelDeployer:
    if settings.DEPLOY_STUB or not settings.VERCEL_TOKEN:
        return MockVercelDeployer(domain_suffix=settings.PRIMARY_DOMAIN_SUFFIX)
    return LiveVercelDeployer(settings)
