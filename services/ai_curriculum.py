
"""ai_curriculum.py - AI summary, difficulty, and programme generation."""

import logging

from services.ai_core import (
    FALLBACK_SUMMARY,
    _brief_error,
    _clear_error,
    _generate_text,
    _parse_json_response,
    _remember_error,
)

logger = logging.getLogger(__name__)

def summarize(text: str, api_key: str = None) -> tuple:
    """
    Summarize course material text using the configured AI provider.

    Returns:
        tuple of (summary: str, used_fallback: bool)
    """
    summary = _generate_text(
        (
            "You are a helpful academic assistant. Summarize the following "
            "course material in one concise paragraph (3-5 sentences). Focus "
            "on what the student will learn and the key topics covered."
        ),
        text,
        max_tokens=300,
        temperature=0.5,
        api_key=api_key,
    )
    if summary:
        return (summary, False)
    logger.info("AI summary unavailable - using fallback summary.")
    return (FALLBACK_SUMMARY, True)


def analyze_course_difficulty(
    course: dict,
    material_text: str,
    summary: str,
    api_key: str = None,
) -> tuple:
    """
    Analyze course difficulty with the configured AI provider.

    Returns:
        tuple of (data: dict with level/rationale/signals, used_fallback: bool)
    """
    course_name = course.get("course_name", "")
    course_description = course.get("description", "")
    keywords = ", ".join(course.get("keywords", []))
    material_preview = (material_text or "")[:3500]

    prompt = f"""Analyze the difficulty of this short programme source course.

Course name: {course_name}
Description: {course_description}
Keywords: {keywords}
Material summary: {summary}
Material excerpt: {material_preview}

Classify the learner difficulty as exactly one of: Easy, Medium, Hard.

Use this rubric:
- Easy: beginner friendly, low prerequisite knowledge, mostly conceptual or guided practice
- Medium: some technical concepts, practice tasks, or tool use but still accessible with guidance
- Hard: advanced prerequisites, dense technical depth, independent complex projects, or specialist knowledge

Return ONLY valid JSON with this structure:
{{
  "level": "Easy | Medium | Hard",
  "rationale": "One concise sentence explaining why",
  "signals": ["Signal 1", "Signal 2", "Signal 3"]
}}"""

    raw = _generate_text(
        "You are a university curriculum analyst. Always respond with valid JSON only.",
        prompt,
        max_tokens=700,
        temperature=0.25,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (
            {
                "level": "Medium",
                "rationale": "The course combines beginner concepts with practical tool-based project work.",
                "signals": ["Beginner-facing source course", "Hands-on project work", "Guided short programme format"],
            },
            True,
        )

    try:
        data = _parse_json_response(raw)
        level = str(data.get("level", "Medium")).strip().title()
        if level not in {"Easy", "Medium", "Hard"}:
            level = "Medium"
        data["level"] = level
        data["rationale"] = data.get("rationale") or "The course has a balanced mix of theory and applied tasks."
        data["signals"] = data.get("signals") or []
        _clear_error()
        return (data, False)
    except Exception as e:
        logger.warning("AI difficulty parse error (%s) - using fallback.", e)
        _remember_error(_brief_error("AI", "Could not parse AI difficulty response", e))
        return (
            {
                "level": "Medium",
                "rationale": "The course combines beginner concepts with practical tool-based project work.",
                "signals": ["Beginner-facing source course", "Hands-on project work", "Guided short programme format"],
            },
            True,
        )


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
    """
    Generate a short programme plan using the configured AI provider.

    Returns:
        tuple of (programme: dict, used_fallback: bool)
    """
    teacher_name = teacher.get("name", "")
    available_months = teacher.get("available_months", [])
    course_name = course.get("course_name", "")
    trend_name = trend.get("trend", "")
    keywords = ", ".join(trend.get("keywords", []))
    approach_instruction = (
        f"\nAlternative approach requested: {approach}. Make the whole programme structure, framing, title, outcomes, weekly activities, and assessment reflect this approach while staying credible for Xamk."
        if approach
        else ""
    )

    prompt = f"""Create a demo-ready university short programme plan.

Matched course: {course_name}
Trend: {trend_name}
Trend keywords: {keywords}
Recommended duration: {weeks} weeks
Credits: {ects} ECTS
Teacher: {teacher_name}
Available months: {", ".join(available_months)}
Course material summary: {summary}
{approach_instruction}

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
  "learning_outcomes": [
    "Outcome 1",
    "Outcome 2",
    "Outcome 3"
  ],
  "weekly_structure": {{
    "Week 1": [
      "Topic title - concrete activity students do",
      "Topic title - concrete activity students do",
      "Topic title - concrete activity students do"
    ]
  }},
  "assessment": "Short description of how students complete the 3 ECTS work",
  "demo_pitch": "One persuasive sentence explaining why this programme should run now"
}}

Make the programme feel current, practical, and credible for Xamk continuing education. Create exactly {weeks} week entries."""

    raw = _generate_text(
        "You are a senior curriculum designer for Xamk short programmes. Always respond with valid JSON only.",
        prompt,
        max_tokens=1800,
        temperature=0.65,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        required = ["title", "weekly_structure", "target_students"]
        if all(data.get(key) for key in required):
            data["based_on"] = data.get("based_on") or course_name
            data["ects"] = data.get("ects") or ects
            data["duration_weeks"] = data.get("duration_weeks") or weeks
            data["teacher"] = data.get("teacher") or teacher_name
            data["teacher_id"] = data.get("teacher_id") or teacher.get("teacher_id", "")
            data["available_months"] = data.get("available_months") or available_months
            data["mode"] = data.get("mode") or "Online / Hybrid"
            logger.info("AI programme generated successfully.")
            _clear_error()
            return (data, False)
        _remember_error("AI programme response was missing required fields.")
        return (None, True)
    except Exception as e:
        logger.warning("AI programme parse error (%s) - using fallback.", e)
        _remember_error(_brief_error("AI", "Could not parse AI programme response", e))
        return (None, True)


