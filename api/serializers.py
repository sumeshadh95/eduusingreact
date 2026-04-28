"""Conversion helpers between backend snake_case and React camelCase payloads."""

from typing import Any


def camel_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "size": analysis.get("size", ""),
        "weeks": analysis.get("weeks", 0),
        "ects": analysis.get("ects", 3),
        "wordCount": analysis.get("word_count", analysis.get("wordCount", 0)),
    }


def snake_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "size": analysis.get("size", ""),
        "weeks": analysis.get("weeks", 0),
        "ects": analysis.get("ects", 3),
        "word_count": analysis.get("word_count", analysis.get("wordCount", 0)),
    }


def camel_programme(programme: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": programme.get("title", ""),
        "basedOn": programme.get("based_on", programme.get("basedOn", "")),
        "ects": programme.get("ects", 3),
        "durationWeeks": programme.get("duration_weeks", programme.get("durationWeeks", 0)),
        "mode": programme.get("mode", ""),
        "teacher": programme.get("teacher", ""),
        "teacherId": programme.get("teacher_id", programme.get("teacherId", "")),
        "availableMonths": programme.get("available_months", programme.get("availableMonths", [])),
        "targetStudents": programme.get("target_students", programme.get("targetStudents", "")),
        "outcomes": programme.get("learning_outcomes", programme.get("outcomes", [])),
        "weeklyStructure": programme.get("weekly_structure", programme.get("weeklyStructure", {})),
        "assessment": programme.get("assessment", ""),
        "demoPitch": programme.get("demo_pitch", programme.get("demoPitch", "")),
    }


def snake_programme(programme: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": programme.get("title", ""),
        "based_on": programme.get("based_on", programme.get("basedOn", "")),
        "ects": programme.get("ects", 3),
        "duration_weeks": programme.get("duration_weeks", programme.get("durationWeeks", 0)),
        "mode": programme.get("mode", ""),
        "teacher": programme.get("teacher", ""),
        "teacher_id": programme.get("teacher_id", programme.get("teacherId", "")),
        "available_months": programme.get("available_months", programme.get("availableMonths", [])),
        "target_students": programme.get("target_students", programme.get("targetStudents", "")),
        "learning_outcomes": programme.get("learning_outcomes", programme.get("outcomes", [])),
        "weekly_structure": programme.get("weekly_structure", programme.get("weeklyStructure", {})),
        "assessment": programme.get("assessment", ""),
        "demo_pitch": programme.get("demo_pitch", programme.get("demoPitch", "")),
    }


def camel_chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    game = chapter.get("minigame", chapter.get("game", {})) or {}
    return {
        "title": chapter.get("title", ""),
        "standard": chapter.get("standard_explanation", chapter.get("standard", "")),
        "personalized": chapter.get("personalized_explanation", chapter.get("personalized", "")),
        "game": {
            "name": game.get("name", ""),
            "description": game.get("description", ""),
            "scenario": game.get("scenario", ""),
            "choices": game.get("choices", []),
            "correctChoice": game.get("correct_choice", game.get("correctChoice", "")),
            "feedback": game.get("feedback", ""),
        },
    }


def snake_chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    game = chapter.get("minigame", chapter.get("game", {})) or {}
    return {
        "title": chapter.get("title", ""),
        "standard_explanation": chapter.get("standard_explanation", chapter.get("standard", "")),
        "personalized_explanation": chapter.get("personalized_explanation", chapter.get("personalized", "")),
        "minigame": {
            "name": game.get("name", ""),
            "description": game.get("description", ""),
            "scenario": game.get("scenario", ""),
            "choices": game.get("choices", []),
            "correct_choice": game.get("correct_choice", game.get("correctChoice", "")),
            "feedback": game.get("feedback", ""),
        },
    }


def camel_personalized(
    chapters: list[dict[str, Any]], final_assignment: str, used_fallback: bool
) -> dict[str, Any]:
    return {
        "studentProfile": "Nursing student interested in IT and electronics",
        "chapters": [camel_chapter(chapter) for chapter in chapters],
        "finalAssignment": final_assignment,
        "usedFallback": used_fallback,
    }


def camel_marketing(content: dict[str, Any], used_fallback: bool = False) -> dict[str, Any]:
    return {
        "website": content.get("website", ""),
        "social": content.get("social", ""),
        "email": content.get("email", ""),
        "tagline": content.get("tagline", ""),
        "sellingPoints": content.get("selling_points", content.get("sellingPoints", [])),
        "usedFallback": used_fallback,
    }


def snake_marketing(content: dict[str, Any]) -> dict[str, Any]:
    return {
        "website": content.get("website", ""),
        "social": content.get("social", ""),
        "email": content.get("email", ""),
        "tagline": content.get("tagline", ""),
        "selling_points": content.get("selling_points", content.get("sellingPoints", [])),
    }


def camel_talent(candidate: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(candidate)
    enriched["matchScore"] = candidate.get("match_score", candidate.get("matchScore", 0))
    enriched["matchReasons"] = candidate.get("match_reasons", candidate.get("matchReasons", []))
    return enriched


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
