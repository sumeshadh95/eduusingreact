"""AI chapter text patch generation."""

import logging

from services.ai_core import _brief_error, _clear_error, _generate_text, _parse_json_response, _remember_error

logger = logging.getLogger(__name__)


def generate_chapter_text_patch(
    course_name: str,
    student_field: str,
    chapter: dict,
    api_key: str = None,
) -> tuple:
    raw = _generate_text(
        "You are an expert instructional designer. Always respond with valid JSON only.",
        chapter_text_prompt(course_name, student_field, chapter),
        max_tokens=850,
        temperature=0.65,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)
    return parse_chapter_text(raw)


def chapter_text_prompt(course_name: str, student_field: str, chapter: dict) -> str:
    game = chapter.get("minigame", {}) or {}
    return f"""Write polished chapter text for an admin-edited personalized learning module.

Course: {course_name}
Student field: {student_field}
Current chapter title: {chapter.get("title", "")}
Current standard explanation: {chapter.get("standard_explanation", "")}
Current personalized explanation: {chapter.get("personalized_explanation", "")}
Mini-game name: {game.get("name", "")}
Mini-game description: {game.get("description", "")}
Mini-game scenario: {game.get("scenario", "")}

Return ONLY valid JSON with this exact structure:
{{
  "title": "Short chapter title",
  "standard_explanation": "A clear 2-3 sentence explanation for any student.",
  "personalized_explanation": "A clear 2-3 sentence explanation that connects the same topic to {student_field} practice."
}}"""


def parse_chapter_text(raw: str) -> tuple:
    try:
        data = _parse_json_response(raw)
        required = ["title", "standard_explanation", "personalized_explanation"]
        if all(str(data.get(key, "")).strip() for key in required):
            _clear_error()
            return (data, False)
        _remember_error("AI chapter text response was missing title or explanations.")
    except Exception as exc:
        logger.warning("AI chapter text parse error (%s).", exc)
        _remember_error(_brief_error("AI", "Could not parse AI chapter text response", exc))
    return (None, True)
