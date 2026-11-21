from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from website_agent.application.generator import ContentGenerator, OpenRouterWebsiteCopyClient
from website_agent.config import get_settings
from website_agent.domain.spec import (
    DeploymentResult,
    GenerateWebsiteRequest,
    GenerateWebsiteResponse,
    SiteSpec,
)
from website_agent.persistence.repository import SiteJobRepository
from website_agent.providers.vercel import create_vercel_deployer
from website_agent.quality.checker import WebsiteQualityChecker
from website_agent.rendering.assembler import LayoutAssembler

logger = logging.getLogger("website_agent.api")
settings = get_settings()

site_repo: SiteJobRepository | None = (
    SiteJobRepository(settings.DATABASE_URL) if not settings.USE_IN_MEMORY_REPO else None
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if site_repo:
        await site_repo.initialize()
    yield
    if site_repo:
        await site_repo.close()


app = FastAPI(
    title="Cre8ive District Website Agent",
    description="Autonomous brand-matched website generation and deployment service",
    version="0.1.0",
    lifespan=lifespan,
)

cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
copy_client = (
    None
    if settings.AI_STUB
    else OpenRouterWebsiteCopyClient(
        settings.OPENROUTER_API_KEY, settings.OPENROUTER_API_BASE, settings.WEBSITE_MODEL
    )
)
generator = ContentGenerator(stub_mode=settings.AI_STUB, llm_client=copy_client)
assembler = LayoutAssembler()
quality_checker = WebsiteQualityChecker()
deployer = create_vercel_deployer(settings)

# In-memory storage for preview and deployment
_generated_sites: dict[UUID, SiteSpec] = {}
_generated_files: dict[UUID, dict[str, str]] = {}


async def require_service_key(
    x_agent_key: str | None = Header(default=None, alias="X-Agent-Key"),
) -> None:
    if settings.ENV == "production" or settings.SERVICE_API_KEY:
        if not x_agent_key or x_agent_key != settings.SERVICE_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing service key",
            )


class DeployRequest(BaseModel):
    site_id: UUID


@app.get("/health", tags=["health"])
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "ai_stub": settings.AI_STUB,
        "deploy_stub": settings.DEPLOY_STUB,
        "domain_suffix": settings.PRIMARY_DOMAIN_SUFFIX,
    }


@app.get("/v1/ping", tags=["health"], dependencies=[Depends(require_service_key)])
async def ping() -> dict[str, Any]:
    """Authenticated liveness probe: proves reachability and key agreement."""
    return {"status": "ok", "service": settings.SERVICE_NAME}


@app.get("/ready", tags=["health"])
async def ready() -> dict[str, Any]:
    if site_repo:
        try:
            from sqlalchemy import text

            async with site_repo._session_factory() as session:
                await session.execute(text("SELECT 1"))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database unreachable: {exc}",
            ) from exc
    return {"status": "ready", "service": settings.SERVICE_NAME}


@app.post(
    "/v1/websites/generate",
    response_model=GenerateWebsiteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["websites"],
    dependencies=[Depends(require_service_key)],
)
async def generate_website(payload: GenerateWebsiteRequest) -> GenerateWebsiteResponse:
    # 1. Generate SiteSpec
    spec = await generator.generate_site_spec(
        brand=payload.brand,
        business=payload.business,
        theme=payload.theme,
        subdomain=payload.subdomain,
    )

    # 2. Assemble file tree
    files = assembler.assemble(spec)

    # 3. Quality check
    quality_report = quality_checker.check(files)

    # Store for preview/deploy
    _generated_sites[spec.site_id] = spec
    _generated_files[spec.site_id] = files

    if site_repo:
        try:
            await site_repo.save_site(
                site_id=spec.site_id,
                business_id=payload.business.business_id,
                spec_dict=spec.model_dump(mode="json"),
                files_dict=files,
                quality_dict=quality_report.model_dump(mode="json"),
            )
        except Exception as exc:
            if settings.ENV == "production":
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to persist site to repository: {exc}",
                ) from exc
            logger.warning("Could not persist site to repository: %s", exc)

    page_slugs = [p.slug for p in spec.pages]

    return GenerateWebsiteResponse(
        site_id=spec.site_id,
        spec=spec,
        pages=page_slugs,
        quality=quality_report,
        preview_url=f"/v1/websites/{spec.site_id}/preview/index",
        deployment=None,
    )


@app.post(
    "/v1/websites/deploy",
    response_model=DeploymentResult,
    tags=["websites"],
    dependencies=[Depends(require_service_key)],
)
async def deploy_website(payload: DeployRequest) -> DeploymentResult:
    site = _generated_sites.get(payload.site_id)
    files = _generated_files.get(payload.site_id)

    if (not site or not files) and site_repo:
        job = await site_repo.get_site(payload.site_id)
        if job and job.spec_json and job.files_json:
            site = SiteSpec.model_validate(job.spec_json)
            files = job.files_json
            _generated_sites[payload.site_id] = site
            _generated_files[payload.site_id] = files

    if not site or not files:
        raise HTTPException(
            status_code=404,
            detail=f"Site with id {payload.site_id} not found. Generate the site first.",
        )

    result = await deployer.deploy(site, files)

    if site_repo:
        try:
            await site_repo.update_deployment(
                site_id=payload.site_id,
                deployment_dict=result.model_dump(mode="json"),
            )
        except Exception as exc:
            if settings.ENV == "production":
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to persist deployment to repository: {exc}",
                ) from exc
            logger.warning("Could not persist deployment to repository: %s", exc)

    return result


@app.post(
    "/v1/websites/generate-and-deploy",
    response_model=GenerateWebsiteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["websites"],
    dependencies=[Depends(require_service_key)],
)
async def generate_and_deploy(payload: GenerateWebsiteRequest) -> GenerateWebsiteResponse:
    # 1. Generate
    gen_response = await generate_website(payload)

    # 2. Deploy
    site = _generated_sites[gen_response.site_id]
    files = _generated_files[gen_response.site_id]
    try:
        deployment = await deployer.deploy(site, files)
    except Exception as exc:
        if site_repo:
            await site_repo.update_failure(gen_response.site_id)
        logger.exception("Website deployment failed for site %s", gen_response.site_id)
        raise HTTPException(status_code=502, detail="Website deployment failed") from exc

    gen_response.deployment = deployment

    if site_repo:
        try:
            await site_repo.update_deployment(
                site_id=gen_response.site_id,
                deployment_dict=deployment.model_dump(mode="json"),
            )
        except Exception as exc:
            if settings.ENV == "production":
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to persist deployment to repository: {exc}",
                ) from exc
            logger.warning("Could not persist deployment to repository: %s", exc)

    return gen_response


@app.get(
    "/v1/websites/{site_id}/preview/{page_slug}",
    response_class=HTMLResponse,
    tags=["preview"],
)
async def preview_page(site_id: UUID, page_slug: str) -> HTMLResponse:
    files = _generated_files.get(site_id)
    if not files and site_repo:
        job = await site_repo.get_site(site_id)
        if job and job.files_json:
            files = job.files_json
            _generated_files[site_id] = files

    if not files:
        raise HTTPException(status_code=404, detail="Site not found")

    filename = f"{page_slug}.html" if not page_slug.endswith(".html") else page_slug
    content = files.get(filename)
    if not content:
        raise HTTPException(status_code=404, detail=f"Page {filename} not found")

    return HTMLResponse(content=content)


@app.get(
    "/v1/websites/{site_id}/files", tags=["websites"], dependencies=[Depends(require_service_key)]
)
async def list_files(site_id: UUID) -> dict[str, list[str]]:
    files = _generated_files.get(site_id)
    if not files and site_repo:
        job = await site_repo.get_site(site_id)
        if job and job.files_json:
            files = job.files_json
            _generated_files[site_id] = files

    if not files:
        raise HTTPException(status_code=404, detail="Site not found")
    return {"files": list(files.keys())}
