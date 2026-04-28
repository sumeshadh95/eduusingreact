"""Programme-generation response parsing."""

import logging

from services.ai_core import _brief_error, _clear_error, _parse_json_response, _remember_error

logger = logging.getLogger(__name__)


def parse_programme(raw: str, course: dict, teacher: dict, weeks: int, ects: int) -> tuple:
    try:
        data = _parse_json_response(raw)
        if has_required_programme_fields(data):
            normalize_programme(data, course, teacher, weeks, ects)
            logger.info("AI programme generated successfully.")
            _clear_error()
            return (data, False)
        _remember_error("AI programme response was missing required fields.")
    except Exception as exc:
        logger.warning("AI programme parse error (%s) - using fallback.", exc)
        _remember_error(_brief_error("AI", "Could not parse AI programme response", exc))
    return (None, True)


def has_required_programme_fields(data: dict) -> bool:
    return all(data.get(key) for key in ["title", "weekly_structure", "target_students"])


def normalize_programme(data: dict, course: dict, teacher: dict, weeks: int, ects: int) -> None:
    for key, fallback in programme_defaults(course, teacher, weeks, ects).items():
        if not data.get(key):
            data[key] = fallback


def programme_defaults(course: dict, teacher: dict, weeks: int, ects: int) -> dict:
    return {
        "based_on": course.get("course_name", ""),
        "ects": ects,
        "duration_weeks": weeks,
        "teacher": teacher.get("name", ""),
        "teacher_id": teacher.get("teacher_id", ""),
        "available_months": teacher.get("available_months", []),
        "mode": "Online / Hybrid",
    }
