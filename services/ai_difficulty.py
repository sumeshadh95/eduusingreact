"""AI course difficulty analysis."""

import logging

from services.ai_core import _brief_error, _clear_error, _generate_text, _parse_json_response, _remember_error

logger = logging.getLogger(__name__)

FALLBACK_DIFFICULTY = {
    "level": "Medium",
    "rationale": "The course combines beginner concepts with practical tool-based project work.",
    "signals": ["Beginner-facing source course", "Hands-on project work", "Guided short programme format"],
}


def analyze_course_difficulty(
    course: dict,
    material_text: str,
    summary: str,
    api_key: str = None,
) -> tuple:
    raw = _generate_text(
        "You are a university curriculum analyst. Always respond with valid JSON only.",
        difficulty_prompt(course, material_text, summary),
        max_tokens=700,
        temperature=0.25,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (dict(FALLBACK_DIFFICULTY), True)
    return parse_difficulty(raw)


def difficulty_prompt(course: dict, material_text: str, summary: str) -> str:
    return f"""Analyze the difficulty of this short programme source course.

Course name: {course.get("course_name", "")}
Description: {course.get("description", "")}
Keywords: {", ".join(course.get("keywords", []))}
Material summary: {summary}
Material excerpt: {(material_text or "")[:3500]}

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


def parse_difficulty(raw: str) -> tuple:
    try:
        data = _parse_json_response(raw)
        data["level"] = normalized_level(data.get("level", "Medium"))
        data["rationale"] = data.get("rationale") or "The course has a balanced mix of theory and applied tasks."
        data["signals"] = data.get("signals") or []
        _clear_error()
        return (data, False)
    except Exception as exc:
        logger.warning("AI difficulty parse error (%s) - using fallback.", exc)
        _remember_error(_brief_error("AI", "Could not parse AI difficulty response", exc))
        return (dict(FALLBACK_DIFFICULTY), True)


def normalized_level(level: str) -> str:
    value = str(level or "Medium").strip().title()
    return value if value in {"Easy", "Medium", "Hard"} else "Medium"
