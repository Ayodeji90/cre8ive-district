from __future__ import annotations

import enum
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class RunStatus(str, enum.Enum):
    STARTING = "starting"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, enum.Enum):
    BRAND_IMPROVEMENT = "brand_improvement"
    WEBSITE_IMPROVEMENT = "website_improvement"
    SOCIAL_POST = "social_post"
    OUTREACH_EMAIL = "outreach_email"
    COMPETITOR_RESEARCH = "competitor_research"
    CONTENT_CREATION = "content_creation"
    SEO_OPTIMIZATION = "seo_optimization"
    ANALYTICS_REVIEW = "analytics_review"


class TaskStatus(str, enum.Enum):
    PLANNED = "planned"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ApprovalMode(str, enum.Enum):
    ASK_FIRST = "ask_first"
    ON_ITS_OWN = "on_its_own"


class RunEventType(str, enum.Enum):
    RUN_STARTED = "run_started"
    TASK_PLANNED = "task_planned"
    TASK_EXECUTING = "task_executing"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    APPROVAL_REQUESTED = "approval_requested"
    TASK_APPROVED = "task_approved"
    TASK_REJECTED = "task_rejected"
    TASK_SKIPPED = "task_skipped"
    RUN_PAUSED = "run_paused"
    RUN_RESUMED = "run_resumed"
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXHAUSTED = "budget_exhausted"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    BRIEF_SENT = "brief_sent"


class ChannelPermissions(BaseModel):
    website: ApprovalMode = ApprovalMode.ASK_FIRST
    social_instagram: ApprovalMode = ApprovalMode.ASK_FIRST
    social_facebook: ApprovalMode = ApprovalMode.ASK_FIRST
    social_linkedin: ApprovalMode = ApprovalMode.ASK_FIRST
    social_x: ApprovalMode = ApprovalMode.ASK_FIRST
    social_tiktok: ApprovalMode = ApprovalMode.ASK_FIRST
    outreach_email: ApprovalMode = ApprovalMode.ASK_FIRST
    content: ApprovalMode = ApprovalMode.ASK_FIRST

    def mode_for(self, channel: str | None) -> ApprovalMode:
        if channel and hasattr(self, channel):
            return getattr(self, channel)
        return ApprovalMode.ASK_FIRST


class CreditBudget(BaseModel):
    total: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.total - self.used)

    @property
    def exhausted(self) -> bool:
        return self.remaining <= 0

    def can_afford(self, cost: int) -> bool:
        return self.remaining >= cost

    def charge(self, cost: int) -> int:
        """Charge credits; returns new used total. Raises ValueError if insufficient."""
        if not self.can_afford(cost):
            raise ValueError(f"Insufficient credits: need {cost}, have {self.remaining}")
        self.used += cost
        return self.used


class BusinessContext(BaseModel):
    """Snapshot of a business's current state for the planner."""

    business_id: UUID
    business_name: str
    business_description: str
    industry: str = ""
    target_audience: str = ""
    # Brand state
    has_brand: bool = False
    brand_quality_score: float | None = None
    brand_summary: str = ""
    # Website state
    has_website: bool = False
    website_url: str = ""
    website_page_count: int = 0
    website_lighthouse_score: float | None = None
    # Social state
    connected_socials: list[str] = Field(default_factory=list)
    recent_posts_count: int = 0
    social_engagement_summary: str = ""
    # Outreach state
    outreach_emails_sent: int = 0
    outreach_reply_rate: float = 0.0
    # Revenue
    total_revenue: float = 0.0
    total_orders: int = 0
    # Competitors
    known_competitors: list[str] = Field(default_factory=list)


class RunTask(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    task_type: TaskType
    status: TaskStatus = TaskStatus.PLANNED
    title: str
    description: str
    reasoning: str = ""
    priority: int = 5
    estimated_credits: int = 5
    actual_credits: int = 0
    channel: str | None = None
    input_data: dict = Field(default_factory=dict)
    output_data: dict = Field(default_factory=dict)
    error_message: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class RunEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    event_type: RunEventType
    message: str
    task_id: UUID | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class Run(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    business_id: UUID
    user_id: UUID
    status: RunStatus = RunStatus.STARTING
    budget: CreditBudget
    permissions: ChannelPermissions = Field(default_factory=ChannelPermissions)
    goal: str = ""
    tasks: list[RunTask] = Field(default_factory=list)
    events: list[RunEvent] = Field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 100
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    paused_at: datetime | None = None
    completed_at: datetime | None = None
    completion_reason: str | None = None
