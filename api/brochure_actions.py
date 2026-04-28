"""Brochure route actions."""

from api.config import effective_api_key, provider_status
from api.serializers import snake_analysis, snake_programme
from services import ai_service


def generate_brochure_payload(programme_payload: dict, course: dict, analysis_payload: dict) -> dict:
    programme = snake_programme(programme_payload)
    analysis = snake_analysis(analysis_payload)
    brochure, used_fallback = ai_service.generate_brochure(
        programme.get("title", ""),
        course.get("course_name", ""),
        analysis["weeks"],
        analysis["ects"],
        programme.get("weekly_structure", {}),
        api_key=effective_api_key(),
    )
    return {
        "ok": bool(brochure and not used_fallback),
        "brochure": brochure or "",
        "usedFallback": used_fallback,
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }
