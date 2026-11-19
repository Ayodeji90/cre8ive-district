"""Bridge between the legacy ``Business`` aggregate and the canonical ``Project``.

The blueprint says "evolve Business rather than creating a parallel projects
record."  Since the Project table (with brand_kits, site_builds, approval_queue,
agent_runs) already exists, the pragmatic path is:

1.  Keep Business as the intake record (chat.py writes to it).
2.  Auto-create / sync a Project when the Business crosses a lifecycle gate
    (e.g. ``status == "ready"``).
3.  New workflows (brand-kit versioning, site builds, approvals, runs) all
    operate on the Project.

This module owns the synchronisation logic.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging import get_logger
from app.models.business import Business
from app.models.project import Project

log = get_logger(__name__)


async def get_or_create_project_for_business(
    db: AsyncSession,
    business: Business,
) -> Project:
    """Return the Project linked to *business*, creating one if needed.

    Fields are copied from the Business on first creation.  Subsequent calls
    return the existing Project without overwriting any user edits.
    """
    # Fast path: project already linked
    existing = await db.scalar(select(Project).where(Project.business_id == business.id))
    if existing is not None:
        return existing

    project = Project(
        user_id=business.owner_id,
        business_id=business.id,
        slug=business.slug,
        name=business.name,
        description=business.description,
        industry=business.industry,
        location=business.location,
        contact_phone=business.contact_phone,
        contact_email=business.contact_email,
        plan=business.plan,
        credit_balance=business.credit_balance,
        status=_map_business_status(business.status),
        preferences=dict(business.preferences or {}),
    )
    db.add(project)
    await db.flush()
    log.info(
        "project_created_from_business",
        project_id=str(project.id),
        business_id=str(business.id),
    )
    return project


async def sync_project_from_business(
    db: AsyncSession,
    business: Business,
) -> Project | None:
    """Push current Business fields into its linked Project.

    Returns ``None`` when no Project exists yet (call
    ``get_or_create_project_for_business`` first if you need one).
    """
    project = await db.scalar(select(Project).where(Project.business_id == business.id))
    if project is None:
        return None

    project.name = business.name
    project.description = business.description
    project.industry = business.industry
    project.location = business.location
    project.contact_phone = business.contact_phone
    project.contact_email = business.contact_email
    project.status = _map_business_status(business.status)
    # Merge preferences (project-side edits win on conflict)
    merged = dict(business.preferences or {})
    merged.update(project.preferences or {})
    project.preferences = merged
    return project


async def get_project_for_business(
    db: AsyncSession,
    business_id: uuid.UUID,
) -> Project | None:
    """Look up the Project linked to a Business id, or ``None``."""
    return await db.scalar(select(Project).where(Project.business_id == business_id))


def _map_business_status(biz_status: str) -> str:
    """Translate legacy Business.status values to Project.status."""
    return {
        "onboarding": "onboarding",
        "ready": "briefing",
        "generating": "generating",
        "review": "review",
        "active": "active",
        "paused": "paused",
    }.get(biz_status, biz_status)
