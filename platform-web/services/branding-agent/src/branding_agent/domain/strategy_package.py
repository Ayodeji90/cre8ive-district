from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from branding_agent.domain.ai_models import BrandStrategy
from branding_agent.domain.brief import CONTRACT_VERSION, BriefSource, NormalizedBrandBrief


class StrategyPackageStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    BLOCKED = "blocked"


class StrategyValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    field: str
    message: str


class StrategyValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    attempts: int = Field(ge=1)
    issues: list[StrategyValidationIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_report(self) -> "StrategyValidationReport":
        if self.passed and self.issues:
            raise ValueError("A passed strategy validation cannot contain issues")
        if not self.passed and not self.issues:
            raise ValueError("A failed strategy validation must contain issues")
        return self


class StrategyPackageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = CONTRACT_VERSION
    brief: NormalizedBrandBrief

    @model_validator(mode="after")
    def require_ready_brief(self) -> "StrategyPackageRequest":
        if self.brief.core_offering is None:
            raise ValueError("A normalized brief with a core offering is required")
        if self.brief.core_offering.source == BriefSource.INFERRED:
            raise ValueError("The core offering must be confirmed by the customer")
        if self.brief.naming_mode == "needs_name_choice":
            raise ValueError("Resolve the business-name choice before strategy generation")
        if self.brief.naming_mode == "existing_name" and self.brief.business_name is None:
            raise ValueError("An existing-name brief must include the supplied business name")
        if (
            self.brief.naming_mode == "existing_name"
            and self.brief.business_name.source == BriefSource.INFERRED
        ):
            raise ValueError("An existing business name must be confirmed by the customer")
        if self.brief.naming_mode == "suggest_names" and self.brief.business_name is not None:
            raise ValueError("A name-suggestion brief must not include an existing business name")
        return self


class StrategyPackageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = CONTRACT_VERSION
    status: StrategyPackageStatus
    brief: NormalizedBrandBrief
    strategy: BrandStrategy | None
    validation: StrategyValidationReport

    @model_validator(mode="after")
    def validate_package_state(self) -> "StrategyPackageResponse":
        if self.status == StrategyPackageStatus.READY_FOR_REVIEW:
            if self.strategy is None or not self.validation.passed:
                raise ValueError("Ready strategy packages require a validated strategy")
        elif self.strategy is not None or self.validation.passed:
            raise ValueError("Blocked strategy packages cannot expose a usable strategy")
        return self
