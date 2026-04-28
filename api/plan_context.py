"""Collect source data needed to build a CoursePilot plan."""

from typing import Any

from services import data_loader
from services import matcher
from services import material_analyzer


def plan_context(trend: dict[str, Any]) -> dict[str, Any]:
    courses = data_loader.load_courses()
    teachers = data_loader.load_teachers()
    match_result = matcher.match_trend_to_course(trend, courses)
    course = selected_course(match_result, courses)
    material_text = data_loader.load_material(course.get("material_file", ""))
    return {
        "trend": trend,
        "courses": courses,
        "teachers": teachers,
        "match_result": match_result,
        "course": course,
        "material_text": material_text,
        "analysis": material_analyzer.analyze(material_text),
        "teacher": find_teacher(course, teachers),
    }


def selected_course(match_result: dict[str, Any], courses: list[dict[str, Any]]) -> dict[str, Any]:
    return match_result.get("course") or first_item(courses)


def find_teacher(course: dict[str, Any], teachers: list[dict[str, Any]]) -> dict[str, Any]:
    teacher_id = course.get("teacher_id", "")
    return next((teacher for teacher in teachers if teacher.get("teacher_id") == teacher_id), first_item(teachers))


def first_item(items: list[dict[str, Any]]) -> dict[str, Any]:
    return items[0] if items else {}
