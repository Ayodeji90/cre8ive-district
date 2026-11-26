from uuid import uuid4

import pytest

from run_engine.domain.credits import (
    affordable_task_types,
)
from run_engine.domain.permissions import needs_approval, task_channel
from run_engine.domain.run import (
    ApprovalMode,
    ChannelPermissions,
    CreditBudget,
    RunTask,
    TaskType,
)


def test_credit_budget_charge_and_exhaustion():
    budget = CreditBudget(total=20, used=0)
    assert budget.remaining == 20
    assert not budget.exhausted
    assert budget.can_afford(15)

    budget.charge(15)
    assert budget.used == 15
    assert budget.remaining == 5
    assert not budget.exhausted
    assert not budget.can_afford(10)

    with pytest.raises(ValueError, match="Insufficient credits"):
        budget.charge(10)

    budget.charge(5)
    assert budget.used == 20
    assert budget.remaining == 0
    assert budget.exhausted


def test_affordable_task_types():
    budget = CreditBudget(total=5, used=0)
    affordable = affordable_task_types(budget)
    assert TaskType.OUTREACH_EMAIL in affordable  # costs 3
    assert TaskType.SOCIAL_POST in affordable  # costs 5
    assert TaskType.BRAND_IMPROVEMENT not in affordable  # costs 10


def test_permissions_channel_mapping():
    assert task_channel(TaskType.WEBSITE_IMPROVEMENT) == "website"
    assert task_channel(TaskType.SEO_OPTIMIZATION) == "website"
    assert task_channel(TaskType.OUTREACH_EMAIL) == "outreach_email"
    assert task_channel(TaskType.SOCIAL_POST, {"platform": "instagram"}) == "social_instagram"
    assert task_channel(TaskType.SOCIAL_POST, {"platform": "x"}) == "social_x"
    assert task_channel(TaskType.BRAND_IMPROVEMENT) is None


def test_needs_approval():
    perms = ChannelPermissions(
        website=ApprovalMode.ASK_FIRST,
        social_instagram=ApprovalMode.ON_ITS_OWN,
    )

    task_web = RunTask(
        run_id=uuid4(),
        task_type=TaskType.WEBSITE_IMPROVEMENT,
        title="Headline update",
        description="",
    )
    assert needs_approval(task_web, perms) is True

    task_insta = RunTask(
        run_id=uuid4(),
        task_type=TaskType.SOCIAL_POST,
        title="IG Post",
        description="",
        input_data={"platform": "instagram"},
    )
    assert needs_approval(task_insta, perms) is False
