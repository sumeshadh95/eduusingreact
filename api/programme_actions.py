"""Regenerate programme route action."""

from api.config import effective_api_key
from api.plan_programme import fallback_programme
from api.route_responses import programme_response
from api.serializers import snake_analysis
from services import ai_service


def regenerate_programme_payload(plan: dict, approach: str) -> dict:
    analysis = snake_analysis(plan.get("analysis", {}))
    programme, used_fallback = ai_service.generate_programme_content(
        plan.get("course", {}),
        plan.get("teacher", {}),
        plan.get("trend", {}),
        analysis["weeks"],
        analysis["ects"],
        plan.get("summary", {}).get("body", ""),
        api_key=effective_api_key(),
        approach=approach.strip() or None,
    )
    if not programme or used_fallback:
        programme = fallback_programme(plan.get("course", {}), plan.get("teacher", {}), analysis)
        used_fallback = True
    return programme_response(programme, used_fallback)
