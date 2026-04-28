"""Programme and marketing generation for plan building."""

from typing import Any

from services import ai_service
from services import course_generator
from services import marketing


def fallback_programme(
    course: dict[str, Any], teacher: dict[str, Any], analysis: dict[str, Any]
) -> dict[str, Any]:
    return course_generator.generate_programme(
        course,
        teacher,
        analysis.get("weeks", 2),
        analysis.get("ects", 3),
    )


def generate_programme(
    course: dict[str, Any],
    teacher: dict[str, Any],
    trend: dict[str, Any],
    analysis: dict[str, Any],
    summary_text: str,
    api_key: str,
) -> tuple[dict[str, Any], bool]:
    programme, used_fallback = ai_service.generate_programme_content(
        course,
        teacher,
        trend,
        analysis["weeks"],
        analysis["ects"],
        summary_text,
        api_key=api_key,
    )
    return (programme, False) if programme and not used_fallback else (fallback_programme(course, teacher, analysis), True)


def generate_marketing(
    programme: dict[str, Any], course: dict[str, Any], analysis: dict[str, Any], api_key: str
) -> tuple[dict[str, Any], bool]:
    content, used_fallback = ai_service.generate_marketing_content(
        programme.get("title", ""),
        course.get("course_name", ""),
        analysis["weeks"],
        analysis["ects"],
        api_key=api_key,
    )
    return (content, False) if content and not used_fallback else (marketing.get_marketing_content(programme), True)
