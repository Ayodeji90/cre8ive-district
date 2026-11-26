"""Unified project router — CRUD for projects, brand kits, site builds,
approval queue, agent runs, and reviews.

All routes are scoped to the authenticated user's projects.

**Transitional**: This router is mounted under ``/api/projects`` but is
NOT yet part of the customer-facing frontend contract.  It is available
for internal testing and backend-to-backend use.  The ``X-Project-API: 1``
header is required while the contract and migration are being verified.
Remove the header gate once the frontend is ready to adopt Project state.
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Business, User
from app.models.project import (
    AgentRun,
    ApprovalItem,
    BrandKit,
    Project,
    RunEvent,
    SiteBuild,
)
from app.models.project_review import ProjectReview
from app.schemas.project import (
    AgentRunCreate,
    AgentRunResponse,
    ApprovalDecision,
    ApprovalItemResponse,
    BrandKitResponse,
    BrandKitUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    RunEventResponse,
    SiteBuildCreate,
    SiteBuildResponse,
)
from app.schemas.project_review import (
    ProjectReviewCreate,
    ProjectReviewDecision,
    ProjectReviewResponse,
)

# ---------------------------------------------------------------------------
# Transitional gate — require X-Project-API header until verified
# ---------------------------------------------------------------------------


async def _require_project_api_header(
    x_project_api: str | None = Header(default=None, alias="X-Project-API"),
) -> None:
    """Block frontend usage until the Project contract is verified.

    Internal callers and tests pass ``X-Project-API: 1``.
    Remove this dependency once the frontend adopts Project state.
    """
    if x_project_api != "1":
        raise HTTPException(
            status_code=400,
            detail="Project API is transitional. Pass X-Project-API: 1 header.",
        )


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(_require_project_api_header)],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_project(db: AsyncSession, project_id: uuid.UUID, user: User) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this project")
    return project


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Project]:
    result = await db.execute(
        select(Project).where(Project.user_id == user.id).order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Project:
    slug = payload.slug or f"proj-{uuid.uuid4().hex[:8]}"
    existing = await db.scalar(select(Project.id).where(Project.slug == slug))
    if existing is not None:
        raise HTTPException(status_code=409, detail="This slug is already taken")

    project = Project(
        user_id=user.id,
        slug=slug,
        name=payload.name,
        description=payload.description,
        industry=payload.industry,
        location=payload.location,
        contact_phone=payload.contact_phone,
        contact_email=payload.contact_email,
        preferences=payload.preferences,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Project:
    return await _get_project(db, project_id, user)


@router.get("/by-business/{business_id}", response_model=ProjectResponse)
async def get_project_by_business(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Project:
    """Look up the Project linked to a legacy Business record."""
    project = await db.scalar(select(Project).where(Project.business_id == business_id))
    if project is None:
        raise HTTPException(status_code=404, detail="No project linked to this business")
    if project.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this project")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Project:
    project = await _get_project(db, project_id, user)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(project, key, value)
    await db.commit()
    await db.refresh(project)
    return project


# ---------------------------------------------------------------------------
# Brand Kits
# ---------------------------------------------------------------------------


@router.get("/{project_id}/brand-kits", response_model=list[BrandKitResponse])
async def list_brand_kits(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[BrandKit]:
    await _get_project(db, project_id, user)
    result = await db.execute(
        select(BrandKit).where(BrandKit.project_id == project_id).order_by(BrandKit.version.desc())
    )
    return list(result.scalars().all())


@router.get("/{project_id}/brand-kits/latest", response_model=BrandKitResponse)
async def get_latest_brand_kit(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BrandKit:
    await _get_project(db, project_id, user)
    kit = await db.scalar(
        select(BrandKit).where(BrandKit.project_id == project_id).order_by(BrandKit.version.desc())
    )
    if kit is None:
        raise HTTPException(status_code=404, detail="No brand kit generated yet")
    return kit


@router.patch("/{project_id}/brand-kits/{kit_id}", response_model=BrandKitResponse)
async def update_brand_kit(
    project_id: uuid.UUID,
    kit_id: uuid.UUID,
    payload: BrandKitUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BrandKit:
    await _get_project(db, project_id, user)
    kit = await db.get(BrandKit, kit_id)
    if kit is None or kit.project_id != project_id:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(kit, key, value)
    await db.commit()
    await db.refresh(kit)
    return kit


# ---------------------------------------------------------------------------
# Site Builds
# ---------------------------------------------------------------------------


@router.get("/{project_id}/site-builds", response_model=list[SiteBuildResponse])
async def list_site_builds(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SiteBuild]:
    await _get_project(db, project_id, user)
    result = await db.execute(
        select(SiteBuild)
        .where(SiteBuild.project_id == project_id)
        .order_by(SiteBuild.version.desc())
    )
    return list(result.scalars().all())


@router.get("/{project_id}/site-builds/latest", response_model=SiteBuildResponse)
async def get_latest_site_build(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SiteBuild:
    await _get_project(db, project_id, user)
    build = await db.scalar(
        select(SiteBuild)
        .where(SiteBuild.project_id == project_id)
        .order_by(SiteBuild.version.desc())
    )
    if build is None:
        raise HTTPException(status_code=404, detail="No site build exists yet")
    return build


@router.post(
    "/{project_id}/site-builds",
    response_model=SiteBuildResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_site_build(
    project_id: uuid.UUID,
    payload: SiteBuildCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SiteBuild:
    await _get_project(db, project_id, user)
    # Auto-increment version
    max_version = await db.scalar(
        select(func.coalesce(func.max(SiteBuild.version), 0)).where(
            SiteBuild.project_id == project_id
        )
    )
    build = SiteBuild(
        project_id=project_id,
        brand_kit_id=payload.brand_kit_id,
        version=(max_version or 0) + 1,
    )
    db.add(build)
    await db.commit()
    await db.refresh(build)
    return build


# ---------------------------------------------------------------------------
# Approval Queue
# ---------------------------------------------------------------------------


@router.get("/{project_id}/approvals", response_model=list[ApprovalItemResponse])
async def list_approvals(
    project_id: uuid.UUID,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ApprovalItem]:
    await _get_project(db, project_id, user)
    stmt = select(ApprovalItem).where(ApprovalItem.project_id == project_id)
    if status_filter == "pending":
        stmt = stmt.where(ApprovalItem.decision.is_(None))
    elif status_filter:
        stmt = stmt.where(ApprovalItem.decision == status_filter)
    stmt = stmt.order_by(ApprovalItem.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{project_id}/approvals/pending", response_model=list[ApprovalItemResponse])
async def list_pending_approvals(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ApprovalItem]:
    await _get_project(db, project_id, user)
    result = await db.execute(
        select(ApprovalItem)
        .where(ApprovalItem.project_id == project_id, ApprovalItem.decision.is_(None))
        .order_by(ApprovalItem.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/{project_id}/approvals/{approval_id}/decide", response_model=ApprovalItemResponse)
async def decide_approval(
    project_id: uuid.UUID,
    approval_id: uuid.UUID,
    payload: ApprovalDecision,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApprovalItem:
    await _get_project(db, project_id, user)
    item = await db.get(ApprovalItem, approval_id)
    if item is None or item.project_id != project_id:
        raise HTTPException(status_code=404, detail="Approval item not found")
    if item.status != "pending":
        raise HTTPException(status_code=409, detail="This approval is no longer pending")

    item.decision = payload.decision
    item.reviewer_id = user.id
    item.decided_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(item)
    return item


# ---------------------------------------------------------------------------
# Agent Runs
# ---------------------------------------------------------------------------


@router.get("/{project_id}/runs", response_model=list[AgentRunResponse])
async def list_runs(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[AgentRun]:
    await _get_project(db, project_id, user)
    result = await db.execute(
        select(AgentRun)
        .where(AgentRun.project_id == project_id)
        .order_by(AgentRun.created_at.desc())
    )
    return list(result.scalars().all())


@router.post(
    "/{project_id}/runs", response_model=AgentRunResponse, status_code=status.HTTP_201_CREATED
)
async def start_run(
    project_id: uuid.UUID,
    payload: AgentRunCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentRun:
    project = await _get_project(db, project_id, user)
    if payload.project_id != project_id:
        raise HTTPException(status_code=400, detail="project_id in body must match the URL")

    business = await db.get(Business, project.business_id) if project.business_id else None
    if business is None:
        raise HTTPException(status_code=409, detail="Project is not linked to a workspace")
    budget = min(payload.credits_budget or business.credit_balance, business.credit_balance)
    if budget < 1:
        raise HTTPException(status_code=402, detail="No credits available for a run")

    run = AgentRun(
        project_id=project_id,
        user_id=user.id,
        goal=payload.goal,
        credits_budget=budget,
        max_iterations=payload.max_iterations,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


@router.get("/{project_id}/runs/{run_id}", response_model=AgentRunResponse)
async def get_run(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentRun:
    await _get_project(db, project_id, user)
    run = await db.get(AgentRun, run_id)
    if run is None or run.project_id != project_id:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{project_id}/runs/{run_id}/events", response_model=list[RunEventResponse])
async def list_run_events(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[RunEvent]:
    await _get_project(db, project_id, user)
    run = await db.get(AgentRun, run_id)
    if run is None or run.project_id != project_id:
        raise HTTPException(status_code=404, detail="Run not found")
    result = await db.execute(
        select(RunEvent).where(RunEvent.agent_run_id == run_id).order_by(RunEvent.seq)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Project Reviews
# ---------------------------------------------------------------------------


@router.get("/{project_id}/reviews", response_model=list[ProjectReviewResponse])
async def list_reviews(
    project_id: uuid.UUID,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ProjectReview]:
    await _get_project(db, project_id, user)
    stmt = select(ProjectReview).where(ProjectReview.project_id == project_id)
    if status_filter:
        stmt = stmt.where(ProjectReview.status == status_filter)
    stmt = stmt.order_by(ProjectReview.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "/{project_id}/reviews",
    response_model=ProjectReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    project_id: uuid.UUID,
    payload: ProjectReviewCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProjectReview:
    await _get_project(db, project_id, user)

    # Validate that exactly one deliverable is specified
    if not payload.brand_kit_id and not payload.site_build_id:
        raise HTTPException(status_code=400, detail="Specify brand_kit_id or site_build_id")
    if payload.brand_kit_id and payload.site_build_id:
        raise HTTPException(
            status_code=400, detail="Specify only one of brand_kit_id or site_build_id"
        )

    # Resolve the deliverable version
    version = 1
    if payload.brand_kit_id:
        kit = await db.get(BrandKit, payload.brand_kit_id)
        if kit is None or kit.project_id != project_id:
            raise HTTPException(status_code=404, detail="Brand kit not found")
        version = kit.version
    elif payload.site_build_id:
        build = await db.get(SiteBuild, payload.site_build_id)
        if build is None or build.project_id != project_id:
            raise HTTPException(status_code=404, detail="Site build not found")
        version = build.version

    review = ProjectReview(
        project_id=project_id,
        brand_kit_id=payload.brand_kit_id,
        site_build_id=payload.site_build_id,
        review_type=payload.review_type,
        notes=payload.notes,
        deliverable_version=version,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@router.post(
    "/{project_id}/reviews/{review_id}/decide",
    response_model=ProjectReviewResponse,
)
async def decide_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    payload: ProjectReviewDecision,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProjectReview:
    await _get_project(db, project_id, user)
    review = await db.get(ProjectReview, review_id)
    if review is None or review.project_id != project_id:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.status not in ("pending", "in_review"):
        raise HTTPException(status_code=409, detail="This review has already been decided")

    from datetime import datetime

    review.status = payload.decision
    review.notes = payload.notes or review.notes
    review.revision_instructions = payload.revision_instructions
    review.reviewer_id = user.id
    review.reviewed_at = datetime.now(UTC)

    # When approved, update the deliverable status
    if payload.decision == "approved":
        if review.brand_kit_id:
            kit = await db.get(BrandKit, review.brand_kit_id)
            if kit:
                kit.status = "approved"
        elif review.site_build_id:
            build = await db.get(SiteBuild, review.site_build_id)
            if build and build.build_status == "preview_ready":
                build.build_status = "publishing"

    # When revision_requested, mark deliverable for rework
    elif payload.decision == "revision_requested":
        if review.brand_kit_id:
            kit = await db.get(BrandKit, review.brand_kit_id)
            if kit:
                kit.status = "revision_requested"
        elif review.site_build_id:
            build = await db.get(SiteBuild, review.site_build_id)
            if build:
                build.build_status = "queued"
                build.build_error = None

    await db.commit()
    await db.refresh(review)
    return review
