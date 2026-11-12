from branding_agent.domain.ai_models import BrandStrategy
from branding_agent.domain.brief import BriefSource, NormalizedBrandBrief, TrackedFact
from branding_agent.domain.strategy_package import (
    StrategyPackageResponse,
    StrategyPackageStatus,
    StrategyValidationIssue,
    StrategyValidationReport,
)
from branding_agent.workflows.protocol import BrandingAI

MAX_STRATEGY_ATTEMPTS = 3
MAX_TAGLINE_WORDS = 8
GENERIC_POSITIONING_PHRASES = (
    "quality service",
    "best in class",
    "your trusted partner",
    "delivering excellence",
    "committed to quality",
    "your reliable partner",
    "providing premium services",
)
GENERIC_VOICE_ATTRIBUTES = {
    "professional",
    "reliable",
    "trustworthy",
    "dedicated",
    "quality",
}


def _value(fact: TrackedFact | None) -> str | None:
    return fact.value.strip() if fact is not None else None


def _confirmed_value(fact: TrackedFact | None) -> str | None:
    if fact is None or fact.source == BriefSource.INFERRED:
        return None
    return _value(fact)


def _list_values(facts: list[TrackedFact], *, inferred: bool = False) -> list[str]:
    return [
        fact.value.strip()
        for fact in facts
        if fact.value.strip() and (fact.source == BriefSource.INFERRED) == inferred
    ]


def _inferred_assumptions(brief: NormalizedBrandBrief) -> list[str]:
    assumptions = []
    for field in (
        "business_name",
        "industry",
        "target_audience",
        "market_or_geography",
        "desired_mood",
    ):
        fact = getattr(brief, field)
        if fact is not None and fact.source == BriefSource.INFERRED:
            assumptions.append(f"{field}: {fact.value} (rationale: {fact.rationale})")
    for field in (
        "products_or_services",
        "brand_personality",
        "style_keywords",
        "differentiators",
        "must_avoid",
    ):
        for fact in getattr(brief, field):
            if fact.source == BriefSource.INFERRED:
                assumptions.append(f"{field}: {fact.value} (rationale: {fact.rationale})")
    return assumptions


def validate_strategy(
    brief: NormalizedBrandBrief, strategy: BrandStrategy
) -> list[StrategyValidationIssue]:
    issues: list[StrategyValidationIssue] = []

    def add(code: str, field: str, message: str) -> None:
        issues.append(StrategyValidationIssue(code=code, field=field, message=message))

    for field in (
        "primary_name",
        "positioning",
        "tagline",
        "brand_story",
        "elevator_pitch",
        "target_description",
    ):
        if not getattr(strategy, field).strip():
            add("required_text_missing", field, f"{field} must not be blank.")

    provided_name = _value(brief.business_name)
    if provided_name and strategy.primary_name.strip() != provided_name:
        add(
            "provided_name_changed",
            "primary_name",
            "The supplied business name must be preserved exactly.",
        )

    if len(strategy.tagline.split()) > MAX_TAGLINE_WORDS:
        add(
            "tagline_too_long",
            "tagline",
            f"Tagline must contain no more than {MAX_TAGLINE_WORDS} words.",
        )

    voice = [attribute.strip().casefold() for attribute in strategy.voice_attributes]
    if not 3 <= len(voice) <= 5:
        add("voice_attribute_count", "voice_attributes", "Provide 3 to 5 voice attributes.")
    if any(not attribute for attribute in voice) or len(set(voice)) != len(voice):
        add(
            "voice_attributes_not_distinct",
            "voice_attributes",
            "Voice attributes must be non-empty and distinct.",
        )
    if len(GENERIC_VOICE_ATTRIBUTES.intersection(voice)) >= 2:
        add(
            "voice_attributes_generic",
            "voice_attributes",
            "Replace generic attributes with distinctive brand-specific language.",
        )

    positioning = strategy.positioning.casefold()
    if any(phrase in positioning for phrase in GENERIC_POSITIONING_PHRASES):
        add(
            "positioning_generic",
            "positioning",
            "Positioning must describe a specific point of difference, not a generic promise.",
        )

    story_sentences = [
        sentence
        for sentence in strategy.brand_story.replace("!", ".").replace("?", ".").split(".")
        if sentence.strip()
    ]
    if len(story_sentences) < 2:
        add(
            "brand_story_too_short",
            "brand_story",
            "Brand story must contain at least two sentences.",
        )

    if len(strategy.elevator_pitch.split()) < 20:
        add(
            "elevator_pitch_too_short",
            "elevator_pitch",
            "Elevator pitch must contain at least 20 words.",
        )

    if len(strategy.target_description.split()) < 5:
        add(
            "target_description_too_generic",
            "target_description",
            "Describe the audience with at least five words and a meaningful customer context.",
        )

    keywords = [keyword.strip().casefold() for keyword in strategy.industry_keywords]
    if not 8 <= len(keywords) <= 12:
        add(
            "keyword_count",
            "industry_keywords",
            "Provide 8 to 12 relevant industry and audience keywords.",
        )
    if any(not keyword for keyword in keywords) or len(set(keywords)) != len(keywords):
        add(
            "keywords_not_distinct",
            "industry_keywords",
            "Keywords must be non-empty and distinct.",
        )

    alternatives = [name.strip().casefold() for name in strategy.name_alternatives]
    if len(alternatives) < 2 or any(not name for name in alternatives):
        add(
            "name_alternatives_missing",
            "name_alternatives",
            "Provide at least two non-empty alternative names.",
        )
    if len(set(alternatives)) != len(alternatives):
        add(
            "name_alternatives_not_distinct",
            "name_alternatives",
            "Alternative names must be distinct.",
        )
    if strategy.primary_name.strip().casefold() in alternatives:
        add(
            "primary_name_repeated",
            "name_alternatives",
            "Alternative names must not repeat the primary name.",
        )

    return issues


def _strategy_inputs(brief: NormalizedBrandBrief) -> tuple[str, str, dict[str, object]]:
    offering = _value(brief.core_offering)
    if not offering:
        raise ValueError("A normalized brief with a core offering is required")
    if brief.core_offering.source == BriefSource.INFERRED:
        raise ValueError("The core offering must be confirmed by the customer")

    services = _list_values(brief.products_or_services)
    description = offering
    if services:
        description = f"{offering}\nProducts and services: {', '.join(services)}"

    industry = _confirmed_value(brief.industry) or "not specified"
    preferences: dict[str, object] = {
        "business_name": _confirmed_value(brief.business_name),
        "target_audience": _confirmed_value(brief.target_audience),
        "market_or_geography": _confirmed_value(brief.market_or_geography),
        "style_keywords": _list_values(brief.style_keywords),
        "mood": _confirmed_value(brief.desired_mood),
        "brand_personality": _list_values(brief.brand_personality),
        "differentiators": _list_values(brief.differentiators),
        "must_avoid": _list_values(brief.must_avoid),
        "naming_mode": brief.naming_mode,
        "inferred_assumptions": _inferred_assumptions(brief),
    }
    return description, industry, preferences


async def generate_strategy_package(
    ai: BrandingAI, brief: NormalizedBrandBrief
) -> StrategyPackageResponse:
    description, industry, preferences = _strategy_inputs(brief)

    for attempt in range(1, MAX_STRATEGY_ATTEMPTS + 1):
        strategy = await ai.generate_strategy(description, industry, preferences)
        issues = validate_strategy(brief, strategy)
        if not issues:
            return StrategyPackageResponse(
                status=StrategyPackageStatus.READY_FOR_REVIEW,
                brief=brief,
                strategy=strategy,
                validation=StrategyValidationReport(passed=True, attempts=attempt),
            )
        if attempt == MAX_STRATEGY_ATTEMPTS:
            return StrategyPackageResponse(
                status=StrategyPackageStatus.BLOCKED,
                brief=brief,
                strategy=None,
                validation=StrategyValidationReport(
                    passed=False,
                    attempts=attempt,
                    issues=issues,
                ),
            )
        preferences["strategy_retry_feedback"] = [
            f"{issue.field}: {issue.message}" for issue in issues
        ]

    raise RuntimeError("Strategy generation finished without a result")
