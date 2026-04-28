"""Build the full CoursePilot plan payload consumed by the React UI."""

from typing import Any

from api.config import effective_api_key, provider_status
from api.market import market_analysis
from api.serializers import (
    camel_analysis,
    camel_marketing,
    camel_personalized,
    camel_programme,
    camel_talent,
    summary_card,
)
from services import ai_service
from services import course_generator
from services import data_loader
from services import marketing
from services import matcher
from services import material_analyzer
from services import personalization
from services import talent_search


def find_teacher(course: dict[str, Any], teachers: list[dict[str, Any]]) -> dict[str, Any]:
    teacher_id = course.get("teacher_id", "")
    return next(
        (teacher for teacher in teachers if teacher.get("teacher_id") == teacher_id),
        teachers[0] if teachers else {},
    )


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
    if programme and not used_fallback:
        return (programme, False)
    return (fallback_programme(course, teacher, analysis), True)


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
    if content and not used_fallback:
        return (content, False)
    return (marketing.get_marketing_content(programme), True)


def build_plan(trend: dict[str, Any]) -> dict[str, Any]:
    api_key = effective_api_key()
    courses = data_loader.load_courses()
    teachers = data_loader.load_teachers()
    match_result = matcher.match_trend_to_course(trend, courses)
    course = match_result.get("course") or (courses[0] if courses else {})
    material_text = data_loader.load_material(course.get("material_file", ""))
    analysis = material_analyzer.analyze(material_text)
    teacher = find_teacher(course, teachers)

    summary_text, summary_used_fallback = ai_service.summarize(material_text, api_key=api_key)
    difficulty, difficulty_used_fallback = ai_service.analyze_course_difficulty(
        course,
        material_text,
        summary_text,
        api_key=api_key,
    )
    programme, programme_used_fallback = generate_programme(
        course,
        teacher,
        trend,
        analysis,
        summary_text,
        api_key,
    )
    chapters, final_assignment, personalization_used_fallback = personalization.get_personalized_chapters(
        course.get("course_name", ""),
        "nursing",
        api_key=api_key,
    )
    marketing_content, marketing_used_fallback = generate_marketing(
        programme,
        course,
        analysis,
        api_key,
    )
    talent_results, talent_status = talent_search.search_probable_teachers(
        course,
        trend,
        programme,
        limit=5,
    )

    return {
        "trend": trend,
        "match": match_payload(match_result),
        "course": course,
        "materialText": material_text,
        "analysis": camel_analysis(analysis),
        "teacher": teacher,
        "teachers": teachers,
        "summary": summary_card(summary_text, course, trend, analysis, match_result),
        "summaryUsedFallback": summary_used_fallback,
        "difficulty": {**difficulty, "usedFallback": difficulty_used_fallback},
        "market": market_analysis(course, trend),
        "programme": camel_programme(programme),
        "programmeUsedFallback": programme_used_fallback,
        "personalized": camel_personalized(
            chapters,
            final_assignment,
            personalization_used_fallback,
        ),
        "marketing": camel_marketing(marketing_content, marketing_used_fallback),
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
