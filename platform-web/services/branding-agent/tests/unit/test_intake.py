import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from branding_agent.application.intake import analyze_brand_brief
from branding_agent.domain.brief import (
    BriefExtraction,
    BriefSource,
    ClarificationQuestion,
    ExtractedFact,
    IntakeRequest,
    IntakeStatus,
)


class RecordingExtractor:
    def __init__(self, extraction: BriefExtraction | None = None) -> None:
        self.extraction = extraction or BriefExtraction.empty()
        self.calls: list[tuple[str | None, dict | None, list[dict]]] = []

    async def extract_brand_brief(self, raw_brief, structured_brief, conversation_history):
        self.calls.append((raw_brief, structured_brief, conversation_history))
        return self.extraction


class FixedExtractor:
    def __init__(self, extraction: BriefExtraction) -> None:
        self.extraction = extraction

    async def extract_brand_brief(self, raw_brief, structured_brief, conversation_history):
        return self.extraction


def make_extraction(**overrides) -> BriefExtraction:
    fields = {
        "business_name": None,
        "core_offering": None,
        "industry": None,
        "target_audience": None,
        "market_or_geography": None,
        "products_or_services": [],
        "brand_personality": [],
        "style_keywords": [],
        "desired_mood": None,
        "differentiators": [],
        "must_avoid": [],
        "clarification_questions": [],
    }
    return BriefExtraction(**(fields | overrides))


@pytest.mark.asyncio
async def test_structured_brief_is_sent_to_llm_and_preserved_as_structured_facts() -> None:
    request = IntakeRequest(
        business_id="biz-123",
        structured_brief={
            "business_name": "Paw & Go",
            "core_offering": "Mobile dog grooming",
        },
    )
    extractor = RecordingExtractor()

    response = await analyze_brand_brief(request, extractor)

    assert response.status == IntakeStatus.READY
    assert response.normalized_brief.business_name.value == "Paw & Go"
    assert response.normalized_brief.business_name.source == BriefSource.STRUCTURED_INPUT
    assert response.normalized_brief.core_offering.value == "Mobile dog grooming"
    assert response.normalized_brief.naming_mode == "existing_name"
    assert response.follow_up_questions == []
    assert len(extractor.calls) == 1
    assert extractor.calls[0][1] == {
        "business_name": "Paw & Go",
        "core_offering": "Mobile dog grooming",
        "products_or_services": [],
        "brand_personality": [],
        "style_keywords": [],
        "differentiators": [],
        "must_avoid": [],
    }


@pytest.mark.asyncio
async def test_missing_offering_returns_clarification_instead_of_guessing() -> None:
    request = IntakeRequest(
        raw_brief="Paw & Go is a new business.",
        allow_name_generation=True,
    )
    extractor = FixedExtractor(
        make_extraction(
            core_offering=ExtractedFact(
                value="Mobile dog grooming",
                evidence=None,
                rationale="This is a common service for a pet business.",
            )
        )
    )

    response = await analyze_brand_brief(request, extractor)

    assert response.status == IntakeStatus.NEEDS_CLARIFICATION
    assert response.normalized_brief.core_offering is None
    assert response.missing_critical_info == ["core_offering"]
    assert response.follow_up_questions == ["What product or service will the business provide?"]
    assert response.clarification_questions[0].field == "core_offering"
    assert response.clarification_questions[0].required_to_proceed is True


@pytest.mark.asyncio
async def test_llm_clarification_options_remain_suggestions_until_user_confirms() -> None:
    initial_request = IntakeRequest(
        structured_brief={
            "business_name": "Paw & Go",
            "core_offering": "Mobile dog grooming",
        }
    )
    question = ClarificationQuestion(
        field="style_keywords",
        question="Which visual direction feels right for the brand?",
        why_it_matters="The visual direction guides the identity design.",
        options=[
            {"label": "Bold", "value": "Bold and expressive"},
            {"label": "Calm", "value": "Calm and reassuring"},
        ],
    )
    first_turn = await analyze_brand_brief(
        initial_request,
        FixedExtractor(make_extraction(clarification_questions=[question])),
    )

    assert first_turn.status == IntakeStatus.NEEDS_CLARIFICATION
    assert first_turn.missing_critical_info == []
    assert first_turn.normalized_brief.style_keywords == []
    assert first_turn.clarification_questions == [question]
    assert first_turn.follow_up_questions == [question.question]

    follow_up_request = IntakeRequest(
        structured_brief={
            "business_name": "Paw & Go",
            "core_offering": "Mobile dog grooming",
        },
        conversation_history=[
            {
                "role": "assistant",
                "content": (
                    "Which visual direction feels right? Options: Bold and expressive; "
                    "Calm and reassuring."
                ),
            },
            {"role": "user", "content": "I choose bold and expressive."},
        ],
    )
    second_turn = await analyze_brand_brief(
        follow_up_request,
        FixedExtractor(
            make_extraction(
                style_keywords=[
                    ExtractedFact(
                        value="Bold and expressive",
                        evidence="bold and expressive",
                        rationale=None,
                    )
                ]
            )
        ),
    )

    assert second_turn.status == IntakeStatus.READY
    assert second_turn.clarification_questions == []
    assert len(second_turn.normalized_brief.style_keywords) == 1
    confirmed_style = second_turn.normalized_brief.style_keywords[0]
    assert confirmed_style.value == "Bold and expressive"
    assert confirmed_style.source == BriefSource.CONVERSATION
    assert confirmed_style.evidence == "bold and expressive"


@pytest.mark.asyncio
async def test_business_name_is_not_inferred_without_customer_evidence() -> None:
    request = IntakeRequest(
        raw_brief="I am planning mobile dog grooming.",
        allow_name_generation=True,
    )
    extractor = FixedExtractor(
        make_extraction(
            business_name=ExtractedFact(
                value="Paw & Go",
                evidence=None,
                rationale="The name sounds suitable for a pet business.",
            ),
            core_offering=ExtractedFact(
                value="Mobile dog grooming",
                evidence="mobile dog grooming",
                rationale=None,
            ),
        )
    )

    response = await analyze_brand_brief(request, extractor)

    assert response.status == IntakeStatus.READY
    assert response.normalized_brief.business_name is None
    assert response.normalized_brief.naming_mode == "suggest_names"


@pytest.mark.asyncio
async def test_unstructured_evidence_is_verified_and_inferences_are_labeled() -> None:
    request = IntakeRequest(
        raw_brief="Paw & Go offers mobile dog grooming in Lagos.",
        allow_name_generation=True,
    )
    extractor = FixedExtractor(
        make_extraction(
            business_name=ExtractedFact(value="Paw & Go", evidence="Paw & Go", rationale=None),
            core_offering=ExtractedFact(
                value="Mobile dog grooming",
                evidence="offers mobile dog grooming",
                rationale=None,
            ),
            target_audience=ExtractedFact(
                value="Busy pet owners",
                evidence=None,
                rationale="Mobile grooming is convenient for time-constrained customers.",
            ),
            industry=ExtractedFact(
                value="Pet care",
                evidence="mobile dog grooming",
                rationale=None,
            ),
        )
    )

    response = await analyze_brand_brief(request, extractor)

    assert response.status == IntakeStatus.READY
    assert response.normalized_brief.business_name.source == BriefSource.UNSTRUCTURED_INPUT
    assert response.normalized_brief.core_offering.source == BriefSource.UNSTRUCTURED_INPUT
    assert response.normalized_brief.industry.source == BriefSource.UNSTRUCTURED_INPUT
    assert response.normalized_brief.target_audience.source == BriefSource.INFERRED
    assert response.normalized_brief.naming_mode == "existing_name"


@pytest.mark.asyncio
async def test_assistant_text_cannot_be_used_as_customer_evidence() -> None:
    request = IntakeRequest(
        conversation_history=[
            {"role": "user", "content": "I want help with my new business."},
            {"role": "assistant", "content": "You said you sell candles."},
        ],
    )
    extractor = FixedExtractor(
        make_extraction(
            core_offering=ExtractedFact(
                value="Handmade candles",
                evidence="sell candles",
                rationale=None,
            )
        )
    )

    response = await analyze_brand_brief(request, extractor)

    assert response.status == IntakeStatus.NEEDS_CLARIFICATION
    assert response.normalized_brief.core_offering is None


def test_intake_request_requires_at_least_one_input_source() -> None:
    with pytest.raises(ValidationError):
        IntakeRequest()


def test_shared_contract_documents_are_valid_json_and_versioned() -> None:
    schema_dir = Path(__file__).parents[4] / "contracts" / "schemas" / "v1"
    for name in (
        "brand-brief.schema.json",
        "intake-request.schema.json",
        "intake-result.schema.json",
    ):
        schema = json.loads((schema_dir / name).read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert "/v1/" in schema["$id"]
