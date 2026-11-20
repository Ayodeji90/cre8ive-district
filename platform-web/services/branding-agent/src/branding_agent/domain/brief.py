from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CONTRACT_VERSION = "1.0.0"


class BriefSource(StrEnum):
    STRUCTURED_INPUT = "structured_input"
    UNSTRUCTURED_INPUT = "unstructured_input"
    CONVERSATION = "conversation"
    INFERRED = "inferred"


class IntakeStatus(StrEnum):
    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"


class ConversationMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: Annotated[str, Field(min_length=1, max_length=10_000)]


class StructuredBrandBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business_name: str | None = Field(default=None, max_length=160)
    core_offering: str | None = Field(default=None, max_length=2_000)
    industry: str | None = Field(default=None, max_length=160)
    target_audience: str | None = Field(default=None, max_length=500)
    market_or_geography: str | None = Field(default=None, max_length=300)
    products_or_services: list[str] = Field(default_factory=list, max_length=20)
    brand_personality: list[str] = Field(default_factory=list, max_length=12)
    style_keywords: list[str] = Field(default_factory=list, max_length=12)
    desired_mood: str | None = Field(default=None, max_length=300)
    differentiators: list[str] = Field(default_factory=list, max_length=12)
    must_avoid: list[str] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def reject_blank_values(self) -> "StructuredBrandBrief":
        for field_name in (
            "business_name",
            "core_offering",
            "industry",
            "target_audience",
            "market_or_geography",
            "desired_mood",
        ):
            value = getattr(self, field_name)
            if value is not None and not value.strip():
                raise ValueError(f"{field_name} must not be blank")

        for field_name in (
            "products_or_services",
            "brand_personality",
            "style_keywords",
            "differentiators",
            "must_avoid",
        ):
            values = getattr(self, field_name)
            if any(not value.strip() for value in values):
                raise ValueError(f"{field_name} items must not be blank")
        return self


class IntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = CONTRACT_VERSION
    business_id: str | None = Field(default=None, max_length=128)
    raw_brief: str | None = Field(default=None, max_length=20_000)
    structured_brief: StructuredBrandBrief | None = None
    conversation_history: list[ConversationMessage] = Field(default_factory=list, max_length=40)
    allow_name_generation: bool = True

    @model_validator(mode="after")
    def require_brief_content(self) -> "IntakeRequest":
        has_raw_brief = self.raw_brief is not None and bool(self.raw_brief.strip())
        has_structured_brief = self.structured_brief is not None and any(
            value is not None and value != []
            for value in self.structured_brief.model_dump(exclude_none=True).values()
        )
        has_user_conversation = any(
            message.role == "user" and message.content.strip()
            for message in self.conversation_history
        )
        if not (has_raw_brief or has_structured_brief or has_user_conversation):
            raise ValueError(
                "Provide raw_brief, structured_brief, or at least one user conversation message"
            )
        return self


class ExtractedFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str = Field(min_length=1, max_length=2_000)
    evidence: str | None = Field(max_length=1_000)
    rationale: str | None = Field(max_length=1_000)

    @model_validator(mode="after")
    def reject_blank_text(self) -> "ExtractedFact":
        if not self.value.strip():
            raise ValueError("value must not be blank")
        for field_name in ("evidence", "rationale"):
            value = getattr(self, field_name)
            if value is not None and not value.strip():
                raise ValueError(f"{field_name} must not be blank when provided")
        return self


class ClarificationOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=120)
    value: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def reject_blank_text(self) -> "ClarificationOption":
        if not self.label.strip() or not self.value.strip():
            raise ValueError("Clarification option text must not be blank")
        return self


class ClarificationQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: Literal[
        "business_name",
        "core_offering",
        "industry",
        "target_audience",
        "market_or_geography",
        "products_or_services",
        "brand_personality",
        "style_keywords",
        "desired_mood",
        "differentiators",
        "must_avoid",
        "other",
    ]
    question: str = Field(min_length=1, max_length=500)
    why_it_matters: str = Field(min_length=1, max_length=500)
    required_to_proceed: bool = False
    options: list[ClarificationOption] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def reject_blank_text(self) -> "ClarificationQuestion":
        if not self.question.strip() or not self.why_it_matters.strip():
            raise ValueError("Clarification question text must not be blank")
        return self


class BriefExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business_name: ExtractedFact | None
    core_offering: ExtractedFact | None
    industry: ExtractedFact | None
    target_audience: ExtractedFact | None
    market_or_geography: ExtractedFact | None
    products_or_services: list[ExtractedFact] = Field(max_length=20)
    brand_personality: list[ExtractedFact] = Field(max_length=12)
    style_keywords: list[ExtractedFact] = Field(max_length=12)
    desired_mood: ExtractedFact | None
    differentiators: list[ExtractedFact] = Field(max_length=12)
    must_avoid: list[ExtractedFact] = Field(max_length=12)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list, max_length=3)

    @classmethod
    def empty(cls) -> "BriefExtraction":
        return cls(
            business_name=None,
            core_offering=None,
            industry=None,
            target_audience=None,
            market_or_geography=None,
            products_or_services=[],
            brand_personality=[],
            style_keywords=[],
            desired_mood=None,
            differentiators=[],
            must_avoid=[],
            clarification_questions=[],
        )


class TrackedFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str = Field(min_length=1, max_length=2_000)
    source: BriefSource
    evidence: str | None = Field(default=None, max_length=1_000)
    rationale: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="after")
    def validate_provenance(self) -> "TrackedFact":
        if not self.value.strip():
            raise ValueError("value must not be blank")
        if self.evidence is not None and not self.evidence.strip():
            raise ValueError("evidence must not be blank when provided")
        if (
            self.source
            in {
                BriefSource.UNSTRUCTURED_INPUT,
                BriefSource.CONVERSATION,
            }
            and not self.evidence
        ):
            raise ValueError("User-provided narrative facts require evidence")
        if self.source == BriefSource.INFERRED and not self.rationale:
            raise ValueError("Inferred facts require a rationale")
        if self.rationale is not None and not self.rationale.strip():
            raise ValueError("rationale must not be blank when provided")
        if self.source == BriefSource.INFERRED and not self.rationale.strip():
            raise ValueError("Inferred facts require a non-blank rationale")
        if self.source != BriefSource.INFERRED and self.rationale:
            raise ValueError("Only inferred facts may include a rationale")
        return self


class NormalizedBrandBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = CONTRACT_VERSION
    business_id: str | None = Field(default=None, max_length=128)
    business_name: TrackedFact | None = None
    core_offering: TrackedFact | None = None
    industry: TrackedFact | None = None
    target_audience: TrackedFact | None = None
    market_or_geography: TrackedFact | None = None
    products_or_services: list[TrackedFact] = Field(default_factory=list)
    brand_personality: list[TrackedFact] = Field(default_factory=list)
    style_keywords: list[TrackedFact] = Field(default_factory=list)
    desired_mood: TrackedFact | None = None
    differentiators: list[TrackedFact] = Field(default_factory=list)
    must_avoid: list[TrackedFact] = Field(default_factory=list)
    naming_mode: Literal["existing_name", "suggest_names", "needs_name_choice"] = "suggest_names"


class IntakeAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = CONTRACT_VERSION
    status: IntakeStatus
    normalized_brief: NormalizedBrandBrief
    missing_critical_info: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list, max_length=3)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def validate_intake_state(self) -> "IntakeAnalysisResponse":
        if self.clarification_questions:
            question_text = [item.question for item in self.clarification_questions]
            if self.follow_up_questions != question_text:
                raise ValueError("follow_up_questions must match clarification question text")
        if self.status == IntakeStatus.READY:
            if (
                self.missing_critical_info
                or self.follow_up_questions
                or self.clarification_questions
            ):
                raise ValueError("Ready intake cannot contain missing fields or questions")
            if self.normalized_brief.core_offering is None:
                raise ValueError("Ready intake requires a core offering")
            if self.normalized_brief.naming_mode == "existing_name":
                if self.normalized_brief.business_name is None:
                    raise ValueError("Existing-name mode requires a business name")
        elif not self.follow_up_questions or not self.clarification_questions:
            raise ValueError("Clarification intake requires at least one question")
        return self
