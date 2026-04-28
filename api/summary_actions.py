"""Regenerate course summary and related plan sections."""

from api.config import effective_api_key, provider_status
from api.market import market_analysis
from api.serializers import camel_personalized, snake_analysis, summary_card
from services import ai_service
from services import personalization


def regenerate_summary_payload(plan: dict) -> dict:
    api_key = effective_api_key()
    course = plan.get("course", {})
    summary_text, used_fallback = ai_service.summarize(plan.get("materialText", ""), api_key=api_key)
    difficulty, difficulty_used_fallback = ai_service.analyze_course_difficulty(
        course,
        plan.get("materialText", ""),
        summary_text,
        api_key=api_key,
    )
    return summary_response(
        plan,
        summary_text,
        used_fallback,
        difficulty,
        difficulty_used_fallback,
        personalized_result(course, api_key),
    )


def personalized_result(course: dict, api_key: str) -> tuple:
    return personalization.get_personalized_chapters(
        course.get("course_name", ""),
        "nursing",
        api_key=api_key,
    )


def summary_response(
    plan: dict,
    summary_text: str,
    summary_used_fallback: bool,
    difficulty: dict,
    difficulty_used_fallback: bool,
    personalized: tuple,
) -> dict:
    chapters, final_assignment, personalization_used_fallback = personalized
    course = plan.get("course", {})
    trend = plan.get("trend", {})
    analysis = snake_analysis(plan.get("analysis", {}))
    return {
        "summary": summary_card(summary_text, course, trend, analysis, plan.get("match", {})),
        "summaryUsedFallback": summary_used_fallback,
        "difficulty": {**difficulty, "usedFallback": difficulty_used_fallback},
        "market": market_analysis(course, trend),
        "personalized": camel_personalized(chapters, final_assignment, personalization_used_fallback),
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }
