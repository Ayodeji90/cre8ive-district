from typing import Protocol

from branding_agent.domain.brief import (
    BriefExtraction,
    BriefSource,
    ClarificationQuestion,
    ExtractedFact,
    IntakeAnalysisResponse,
    IntakeRequest,
    IntakeStatus,
    NormalizedBrandBrief,
    TrackedFact,
)


class BriefExtractor(Protocol):
    async def extract_brand_brief(
        self,
        raw_brief: str | None,
        structured_brief: dict | None,
        conversation_history: list[dict],
    ) -> BriefExtraction: ...


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _explicit_fact(value: str, source: BriefSource, evidence: str | None = None) -> TrackedFact:
    return TrackedFact(value=value.strip(), source=source, evidence=evidence)


def _extracted_fact(
    fact: ExtractedFact | None,
    raw_brief: str,
    user_conversation: str,
    *,
    allow_inference: bool = True,
) -> TrackedFact | None:
    if fact is None or not fact.value.strip():
        return None

    evidence = fact.evidence.strip() if fact.evidence else None
    if evidence:
        normalized_evidence = _normalized_text(evidence)
        if normalized_evidence in _normalized_text(user_conversation):
            return _explicit_fact(fact.value, BriefSource.CONVERSATION, evidence)
        if normalized_evidence in _normalized_text(raw_brief):
            return _explicit_fact(fact.value, BriefSource.UNSTRUCTURED_INPUT, evidence)

    if allow_inference and fact.rationale and fact.rationale.strip():
        return TrackedFact(
            value=fact.value.strip(),
            source=BriefSource.INFERRED,
            rationale=fact.rationale.strip(),
        )
    return None


def _tracked_list(
    structured_values: list[str],
    extracted_values: list[ExtractedFact],
    raw_brief: str,
    user_conversation: str,
    *,
    allow_inference: bool = True,
) -> list[TrackedFact]:
    extracted_facts = [
        fact
        for candidate in extracted_values
        if (
            fact := _extracted_fact(
                candidate,
                raw_brief,
                user_conversation,
                allow_inference=allow_inference,
            )
        )
        is not None
    ]
    conversation_facts = [
        fact for fact in extracted_facts if fact.source == BriefSource.CONVERSATION
    ]
    if conversation_facts:
        return conversation_facts
    if structured_values:
        return [
            _explicit_fact(value, BriefSource.STRUCTURED_INPUT)
            for value in structured_values
            if value.strip()
        ]
    return extracted_facts


async def analyze_brand_brief(
    request: IntakeRequest, extractor: BriefExtractor
) -> IntakeAnalysisResponse:
    structured = request.structured_brief
    structured_data = structured.model_dump(exclude_none=True) if structured else None
    user_messages = [
        message.content for message in request.conversation_history if message.role == "user"
    ]
    raw_brief = request.raw_brief or ""
    user_conversation = "\n".join(user_messages)

    extraction = await extractor.extract_brand_brief(
        request.raw_brief,
        structured_data,
        [message.model_dump() for message in request.conversation_history],
    )

    def scalar(
        field_name: str,
        candidate: ExtractedFact | None,
        *,
        allow_inference: bool = True,
    ) -> TrackedFact | None:
        extracted = _extracted_fact(
            candidate,
            raw_brief,
            user_conversation,
            allow_inference=allow_inference,
        )
        if extracted and extracted.source == BriefSource.CONVERSATION:
            return extracted
        explicit_value = getattr(structured, field_name) if structured else None
        if explicit_value is not None and explicit_value.strip():
            return _explicit_fact(explicit_value, BriefSource.STRUCTURED_INPUT)
        return extracted

    core_offering = scalar("core_offering", extraction.core_offering, allow_inference=False)
    if core_offering is None:
        extracted_products = [
            fact
            for candidate in extraction.products_or_services
            if (
                fact := _extracted_fact(
                    candidate,
                    raw_brief,
                    user_conversation,
                    allow_inference=False,
                )
            )
            is not None
        ]
        core_offering = next(
            (fact for fact in extracted_products if fact.source == BriefSource.CONVERSATION),
            None,
        )
        structured_products = structured.products_or_services if structured else []
        if core_offering is None and structured_products:
            core_offering = _explicit_fact(
                "; ".join(value.strip() for value in structured_products if value.strip()),
                BriefSource.STRUCTURED_INPUT,
            )
        if core_offering is None and extracted_products:
            core_offering = extracted_products[0]

    business_name = scalar("business_name", extraction.business_name, allow_inference=False)
    normalized = NormalizedBrandBrief(
        business_id=request.business_id,
        business_name=business_name,
        core_offering=core_offering,
        industry=scalar("industry", extraction.industry),
        target_audience=scalar("target_audience", extraction.target_audience),
        market_or_geography=scalar("market_or_geography", extraction.market_or_geography),
        products_or_services=_tracked_list(
            structured.products_or_services if structured else [],
            extraction.products_or_services,
            raw_brief,
            user_conversation,
        ),
        brand_personality=_tracked_list(
            structured.brand_personality if structured else [],
            extraction.brand_personality,
            raw_brief,
            user_conversation,
        ),
        style_keywords=_tracked_list(
            structured.style_keywords if structured else [],
            extraction.style_keywords,
            raw_brief,
            user_conversation,
        ),
        desired_mood=scalar("desired_mood", extraction.desired_mood),
        differentiators=_tracked_list(
            structured.differentiators if structured else [],
            extraction.differentiators,
            raw_brief,
            user_conversation,
        ),
        must_avoid=_tracked_list(
            structured.must_avoid if structured else [],
            extraction.must_avoid,
            raw_brief,
            user_conversation,
            allow_inference=False,
        ),
        naming_mode=(
            "existing_name"
            if business_name is not None
            else "suggest_names"
            if request.allow_name_generation
            else "needs_name_choice"
        ),
    )

    missing: list[str] = []
    questions = list(extraction.clarification_questions)
    if core_offering is None:
        missing.append("core_offering")
        if not any(question.field == "core_offering" for question in questions):
            questions.insert(
                0,
                ClarificationQuestion(
                    field="core_offering",
                    question="What product or service will the business provide?",
                    why_it_matters=(
                        "The brand strategy needs a confirmed offer to position the business "
                        "accurately."
                    ),
                    required_to_proceed=True,
                ),
            )
    if business_name is None and not request.allow_name_generation:
        missing.append("business_name_or_naming_permission")
        if not any(question.field == "business_name" for question in questions):
            questions.insert(
                0,
                ClarificationQuestion(
                    field="business_name",
                    question=(
                        "Do you already have a business name, or would you like me to suggest some?"
                    ),
                    why_it_matters=(
                        "A name must be supplied or name suggestions authorized before strategy "
                        "generation."
                    ),
                    required_to_proceed=True,
                ),
            )

    for question in questions:
        if question.required_to_proceed and question.field not in missing:
            missing.append(question.field)
    questions.sort(key=lambda question: not question.required_to_proceed)
    questions = questions[:3]
    question_text = [question.question for question in questions]

    if missing or questions:
        return IntakeAnalysisResponse(
            status=IntakeStatus.NEEDS_CLARIFICATION,
            normalized_brief=normalized,
            missing_critical_info=missing,
            follow_up_questions=question_text,
            clarification_questions=questions,
        )
    return IntakeAnalysisResponse(
        status=IntakeStatus.READY,
        normalized_brief=normalized,
    )
