"""AI-derived pieces of the full plan payload."""

from typing import Any

from api.plan_programme import generate_marketing, generate_programme
from services import ai_service
from services import personalization
from services import talent_search


def plan_ai_results(context: dict[str, Any], api_key: str) -> dict[str, Any]:
    summary_text, summary_used_fallback = ai_service.summarize(context["material_text"], api_key=api_key)
    difficulty, difficulty_used_fallback = ai_service.analyze_course_difficulty(
        context["course"],
        context["material_text"],
        summary_text,
        api_key=api_key,
    )
    programme, programme_used_fallback = generate_programme_from_context(context, summary_text, api_key)
    marketing_content, marketing_used_fallback = generate_marketing(
        programme,
        context["course"],
        context["analysis"],
        api_key,
    )
    return {
        "summary_text": summary_text,
        "summary_used_fallback": summary_used_fallback,
        "difficulty": difficulty,
        "difficulty_used_fallback": difficulty_used_fallback,
        "programme": programme,
        "programme_used_fallback": programme_used_fallback,
        "personalized": personalized_result(context, api_key),
        "marketing_content": marketing_content,
        "marketing_used_fallback": marketing_used_fallback,
        "talent": talent_result(context, programme),
    }


def generate_programme_from_context(context: dict[str, Any], summary_text: str, api_key: str) -> tuple:
    return generate_programme(
        context["course"],
        context["teacher"],
        context["trend"],
        context["analysis"],
        summary_text,
        api_key,
    )


def personalized_result(context: dict[str, Any], api_key: str) -> tuple:
    return personalization.get_personalized_chapters(
        context["course"].get("course_name", ""),
        "nursing",
        api_key=api_key,
    )


def talent_result(context: dict[str, Any], programme: dict[str, Any]) -> tuple:
    return talent_search.search_probable_teachers(
        context["course"],
        context["trend"],
        programme,
        limit=5,
    )
