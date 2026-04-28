"""Assemble the React plan payload."""

from typing import Any

from api.config import provider_status
from api.market import market_analysis
from api.serializers import (
    camel_analysis,
    camel_marketing,
    camel_personalized,
    camel_programme,
    camel_talent,
    summary_card,
)


def plan_payload(context: dict[str, Any], generated: dict[str, Any]) -> dict[str, Any]:
    chapters, final_assignment, personalization_used_fallback = generated["personalized"]
    talent_results, talent_status = generated["talent"]
    return {
        "trend": context["trend"],
        "match": match_payload(context["match_result"]),
        "course": context["course"],
        "materialText": context["material_text"],
        "analysis": camel_analysis(context["analysis"]),
        "teacher": context["teacher"],
        "teachers": context["teachers"],
        "summary": summary_card(
            generated["summary_text"],
            context["course"],
            context["trend"],
            context["analysis"],
            context["match_result"],
        ),
        "summaryUsedFallback": generated["summary_used_fallback"],
        "difficulty": {**generated["difficulty"], "usedFallback": generated["difficulty_used_fallback"]},
        "market": market_analysis(context["course"], context["trend"]),
        "programme": camel_programme(generated["programme"]),
        "programmeUsedFallback": generated["programme_used_fallback"],
        "personalized": camel_personalized(chapters, final_assignment, personalization_used_fallback),
        "marketing": camel_marketing(generated["marketing_content"], generated["marketing_used_fallback"]),
        "talent": [camel_talent(candidate) for candidate in talent_results],
        "talentStatus": talent_status,
        "provider": provider_status(),
    }


def match_payload(match_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "score": match_result.get("score", 0),
        "matchingKeywords": match_result.get("matching_keywords", []),
        "reason": match_result.get("reason", ""),
    }
