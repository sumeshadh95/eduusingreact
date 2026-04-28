"""Summary-card payload serializers."""

from typing import Any


def summary_card(
    summary_text: str,
    course: dict[str, Any],
    trend: dict[str, Any],
    analysis: dict[str, Any],
    match_result: dict[str, Any],
) -> dict[str, Any]:
    keywords = match_result.get("matching_keywords", match_result.get("matchingKeywords", []))
    return {
        "title": f"{course.get('course_name', 'Course')} can become a {analysis.get('weeks', 0)}-week short programme",
        "body": summary_text,
        "highlights": [
            trend_fit_highlight(keywords, trend),
            f"The material maps to {analysis.get('ects', 3)} ECTS across {analysis.get('weeks', 0)} week(s).",
            "The AI output can be regenerated while keeping the source course and trend selection.",
        ],
    }


def trend_fit_highlight(keywords: list[str], trend: dict[str, Any]) -> str:
    if keywords:
        return f"Trend fit is strongest around {', '.join(keywords[:4])}."
    return f"Trend fit is tied to {trend.get('trend', 'the selected topic')}."
