import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from branding_agent.application.strategy import (
    MAX_STRATEGY_ATTEMPTS,
    generate_strategy_package,
    validate_strategy,
)
from branding_agent.domain.ai_models import BrandStrategy
from branding_agent.domain.brief import (
    BriefSource,
    NormalizedBrandBrief,
    TrackedFact,
)
from branding_agent.domain.strategy_package import (
    StrategyPackageRequest,
    StrategyPackageStatus,
)


def fact(value: str) -> TrackedFact:
    return TrackedFact(value=value, source=BriefSource.STRUCTURED_INPUT)


def make_brief(**overrides) -> NormalizedBrandBrief:
    values = {
        "business_name": fact("Paw & Go"),
        "core_offering": fact("Mobile dog grooming"),
        "industry": fact("Pet care"),
        "target_audience": fact("Busy pet owners"),
        "market_or_geography": fact("Lagos, Nigeria"),
        "products_or_services": [fact("At-home grooming")],
        "brand_personality": [fact("Warm"), fact("Confident")],
        "style_keywords": [fact("Modern")],
        "desired_mood": fact("Calm and welcoming"),
        "differentiators": [fact("Grooming at the customer's home")],
        "must_avoid": [],
        "naming_mode": "existing_name",
    }
    return NormalizedBrandBrief(**(values | overrides))


def make_strategy(**overrides) -> BrandStrategy:
    values = {
        "primary_name": "Paw & Go",
        "name_alternatives": ["Pawful Care", "The Grooming Van"],
        "positioning": (
            "A mobile grooming service that brings calm, attentive care to pets at home."
        ),
        "tagline": "Care that comes to you",
        "voice_attributes": ["warm", "confident", "playful"],
        "brand_story": (
            "Paw & Go began when busy Lagos pet owners struggled to find time for grooming. "
            "It brings patient care to the place pets feel safest: home."
        ),
        "elevator_pitch": (
            "Paw & Go brings convenient, patient dog grooming to busy pet owners across Lagos. "
            "By caring for pets in familiar surroundings, it turns a stressful errand into "
            "a calmer experience owners can trust and pets can enjoy."
        ),
        "target_description": (
            "Busy Lagos pet owners who want convenient, low-stress care for their dogs."
        ),
        "industry_keywords": [
            "pet care",
            "dog grooming",
            "mobile grooming",
            "Lagos pets",
            "Nigeria pet services",
            "at-home grooming",
            "pet wellness",
            "convenient grooming",
        ],
    }
    return BrandStrategy(**(values | overrides))


class SequenceStrategyAI:
    def __init__(self, strategies: list[BrandStrategy]) -> None:
        self.strategies = strategies
        self.preferences_seen: list[dict] = []

    async def generate_strategy(self, description, industry, preferences):
        self.preferences_seen.append(preferences.copy())
        return self.strategies.pop(0)


@pytest.mark.asyncio
async def test_strategy_package_returns_validated_strategy_for_review() -> None:
    ai = SequenceStrategyAI([make_strategy()])

    result = await generate_strategy_package(ai, make_brief())

    assert result.status == StrategyPackageStatus.READY_FOR_REVIEW
    assert result.strategy == make_strategy()
    assert result.validation.passed
    assert result.validation.attempts == 1
    assert ai.preferences_seen[0]["business_name"] == "Paw & Go"
    assert ai.preferences_seen[0]["differentiators"] == ["Grooming at the customer's home"]


@pytest.mark.asyncio
async def test_strategy_package_retries_with_validation_feedback() -> None:
    invalid = make_strategy(tagline="This is a very long tagline with too many words")
    ai = SequenceStrategyAI([invalid, make_strategy()])

    result = await generate_strategy_package(ai, make_brief())

    assert result.status == StrategyPackageStatus.READY_FOR_REVIEW
    assert result.validation.attempts == 2
    assert (
        "tagline: Tagline must contain no more than 8 words."
        in ai.preferences_seen[1]["strategy_retry_feedback"]
    )


@pytest.mark.asyncio
async def test_strategy_package_blocks_after_retry_limit_without_returning_bad_strategy() -> None:
    invalid = make_strategy(tagline="This is a very long tagline with too many words")
    ai = SequenceStrategyAI([invalid] * MAX_STRATEGY_ATTEMPTS)

    result = await generate_strategy_package(ai, make_brief())

    assert result.status == StrategyPackageStatus.BLOCKED
    assert result.strategy is None
    assert not result.validation.passed
    assert result.validation.attempts == MAX_STRATEGY_ATTEMPTS
    assert result.validation.issues[0].code == "tagline_too_long"


@pytest.mark.asyncio
async def test_inferred_audience_is_passed_as_a_hypothesis_not_a_confirmed_preference() -> None:
    brief = make_brief(
        target_audience=TrackedFact(
            value="Time-poor pet owners",
            source=BriefSource.INFERRED,
            rationale="Mobile services may appeal to customers with limited time.",
        )
    )
    ai = SequenceStrategyAI([make_strategy()])

    await generate_strategy_package(ai, brief)

    assert ai.preferences_seen[0]["target_audience"] is None
    assert ai.preferences_seen[0]["inferred_assumptions"] == [
        "target_audience: Time-poor pet owners "
        "(rationale: Mobile services may appeal to customers with limited time.)"
    ]


def test_strategy_validator_requires_supplied_business_name_to_be_preserved() -> None:
    issues = validate_strategy(make_brief(), make_strategy(primary_name="Paws & Go"))

    assert [issue.code for issue in issues] == ["provided_name_changed"]

    case_changed = validate_strategy(make_brief(), make_strategy(primary_name="paw & go"))
    assert [issue.code for issue in case_changed] == ["provided_name_changed"]


def test_strategy_request_rejects_brief_without_offering_or_name_choice() -> None:
    with pytest.raises(ValidationError):
        StrategyPackageRequest(brief=make_brief(core_offering=None))

    with pytest.raises(ValidationError):
        StrategyPackageRequest(
            brief=make_brief(
                core_offering=TrackedFact(
                    value="A possible offering",
                    source=BriefSource.INFERRED,
                    rationale="Inferred from the business description.",
                )
            )
        )

    with pytest.raises(ValidationError):
        StrategyPackageRequest(brief=make_brief(naming_mode="needs_name_choice"))

    with pytest.raises(ValidationError):
        StrategyPackageRequest(brief=make_brief(business_name=None, naming_mode="existing_name"))

    with pytest.raises(ValidationError):
        StrategyPackageRequest(brief=make_brief(naming_mode="suggest_names"))

    with pytest.raises(ValidationError):
        StrategyPackageRequest(
            brief=make_brief(
                business_name=TrackedFact(
                    value="Paw & Go",
                    source=BriefSource.INFERRED,
                    rationale="Inferred from the user's business description.",
                )
            )
        )


def test_strategy_package_response_schema_is_valid_and_versioned() -> None:
    schema_path = Path(__file__).parents[4] / "contracts" / "schemas" / "v1"
    for schema_name in ("strategy-package-request.schema.json", "strategy-package.schema.json"):
        schema = json.loads((schema_path / schema_name).read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert "/v1/" in schema["$id"]
