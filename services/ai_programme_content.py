"""AI short-programme content generation."""

import logging

from services.ai_core import _brief_error, _clear_error, _generate_text, _parse_json_response, _remember_error

logger = logging.getLogger(__name__)


def generate_programme_content(
    course: dict,
    teacher: dict,
    trend: dict,
    weeks: int,
    ects: int,
    summary: str,
    api_key: str = None,
    approach: str = None,
) -> tuple:
    raw = _generate_text(
        "You are a senior curriculum designer for Xamk short programmes. Always respond with valid JSON only.",
        programme_prompt(course, teacher, trend, weeks, ects, summary, approach),
        max_tokens=1800,
        temperature=0.65,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)
    return parse_programme(raw, course, teacher, weeks, ects)


def programme_prompt(
    course: dict,
    teacher: dict,
    trend: dict,
    weeks: int,
    ects: int,
    summary: str,
    approach: str = None,
) -> str:
    teacher_name = teacher.get("name", "")
    course_name = course.get("course_name", "")
    return f"""Create a demo-ready university short programme plan.

Matched course: {course_name}
Trend: {trend.get("trend", "")}
Trend keywords: {", ".join(trend.get("keywords", []))}
Recommended duration: {weeks} weeks
Credits: {ects} ECTS
Teacher: {teacher_name}
Available months: {", ".join(teacher.get("available_months", []))}
Course material summary: {summary}
{approach_instruction(approach)}

Return ONLY valid JSON with this exact structure:
{{
  "title": "A concise, marketable programme title",
  "based_on": "{course_name}",
  "ects": {ects},
  "duration_weeks": {weeks},
  "mode": "Online / Hybrid",
  "teacher": "{teacher_name}",
  "teacher_id": "{teacher.get("teacher_id", "")}",
  "available_months": ["month names copied from the teacher availability"],
  "target_students": "Specific target learner group in 1-2 sentences",
  "learning_outcomes": ["Outcome 1", "Outcome 2", "Outcome 3"],
  "weekly_structure": {{"Week 1": ["Topic title - concrete activity students do"]}},
  "assessment": "Short description of how students complete the 3 ECTS work",
  "demo_pitch": "One persuasive sentence explaining why this programme should run now"
}}

Make the programme feel current, practical, and credible for Xamk continuing education. Create exactly {weeks} week entries."""


def approach_instruction(approach: str = None) -> str:
    if not approach:
        return ""
    return (
        f"\nAlternative approach requested: {approach}. Make the whole programme structure, "
        "framing, title, outcomes, weekly activities, and assessment reflect this approach "
        "while staying credible for Xamk."
    )


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
    data["based_on"] = data.get("based_on") or course.get("course_name", "")
    data["ects"] = data.get("ects") or ects
    data["duration_weeks"] = data.get("duration_weeks") or weeks
    data["teacher"] = data.get("teacher") or teacher.get("name", "")
    data["teacher_id"] = data.get("teacher_id") or teacher.get("teacher_id", "")
    data["available_months"] = data.get("available_months") or teacher.get("available_months", [])
    data["mode"] = data.get("mode") or "Online / Hybrid"
