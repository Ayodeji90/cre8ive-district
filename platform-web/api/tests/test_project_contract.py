"""Contract tests for canonical Project linkage and approval lifecycle."""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import ApprovalItem, Business, Project
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_approval_decision_does_not_mark_capability_executed(
    client, session_factory, customer
):
    business = Business(
        owner_id=customer.id,
        name="Contract Workspace",
        slug=f"contract-{uuid.uuid4().hex[:8]}",
    )
    async with session_factory() as db:
        db.add(business)
        await db.flush()
        project = Project(
            user_id=customer.id,
            business_id=business.id,
            slug=f"project-{uuid.uuid4().hex[:8]}",
            name=business.name,
        )
        db.add(project)
        await db.flush()
        item = ApprovalItem(
            project_id=project.id,
            action_type="deploy_site",
            payload_json={"summary": "Publish the approved website"},
        )
        db.add(item)
        await db.commit()
        item_id = item.id
        project_id = project.id

    response = await client.post(
        f"/api/projects/{project_id}/approvals/{item_id}/decide",
        headers={**auth_headers(customer), "X-Project-API": "1"},
        json={"decision": "approved", "reviewer_note": "Looks good"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body == {
        "id": str(item_id),
        "agent_run_id": None,
        "action_type": "deploy_site",
        "summary": "Publish the approved website",
        "decision": "approved",
        "decided_at": body["decided_at"],
        "execution_status": "not_started",
        "executed_at": None,
        "execution_outcome": None,
    }
    assert body["decided_at"] is not None
    async with session_factory() as db:
        saved = await db.scalar(select(ApprovalItem).where(ApprovalItem.id == item_id))
        assert saved is not None
        assert saved.status == "pending"  # decision handler writes decision fields only
        assert saved.reviewer_id == customer.id
        assert saved.decided_at is not None
        assert saved.executed_at is None
        assert saved.execution_outcome is None


@pytest.mark.asyncio
async def test_project_business_link_is_unique(session_factory, customer):
    business = Business(
        owner_id=customer.id,
        name="Unique Workspace",
        slug=f"unique-{uuid.uuid4().hex[:8]}",
    )
    async with session_factory() as db:
        db.add(business)
        await db.flush()
        first = Project(
            user_id=customer.id,
            business_id=business.id,
            slug=f"first-{uuid.uuid4().hex[:8]}",
            name="First",
        )
        db.add(first)
        await db.commit()
        assert first.business_id == business.id
        duplicate = Project(
            user_id=customer.id,
            business_id=business.id,
            slug=f"duplicate-{uuid.uuid4().hex[:8]}",
            name="Duplicate",
        )
        db.add(duplicate)
        with pytest.raises(IntegrityError):
            await db.commit()
        await db.rollback()
