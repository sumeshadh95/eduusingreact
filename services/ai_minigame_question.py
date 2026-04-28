"""AI mini-game question regeneration."""

import logging

from services.ai_core import _brief_error, _clear_error, _generate_text, _parse_json_response, _remember_error

logger = logging.getLogger(__name__)


def generate_minigame_question(
    course_name: str,
    student_field: str,
    chapter: dict,
    api_key: str = None,
) -> tuple:
    raw = _generate_text(
        "You are an educational game designer. Always respond with valid JSON only.",
        minigame_question_prompt(course_name, student_field, chapter),
        max_tokens=900,
        temperature=0.75,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)
    return parse_minigame_question(raw)


def minigame_question_prompt(course_name: str, student_field: str, chapter: dict) -> str:
    return f"""Generate one simple playable mini-game question for this learning chapter.

Course: {course_name}
Student field: {student_field}
Chapter title: {chapter.get("title", "")}
Standard explanation: {chapter.get("standard_explanation", "")}
Personalized explanation: {chapter.get("personalized_explanation", "")}

The question is for an admin-authored personalized learning experience. Make it concrete, useful, and connected to {student_field}. It should be suitable for a student to answer inside a course app.

Return ONLY valid JSON with this exact structure:
{{
  "name": "Short game name",
  "description": "One-sentence description of the mini-game",
  "scenario": "A short decision challenge written as the question the student sees",
  "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
  "correct_choice": "Exact text of the correct choice",
  "feedback": "Brief explanation of why the correct answer is best"
}}"""


def parse_minigame_question(raw: str) -> tuple:
    try:
        data = _parse_json_response(raw)
        choices = data.get("choices", [])
        if data.get("scenario") and len(choices) >= 2:
            data["correct_choice"] = data.get("correct_choice") if data.get("correct_choice") in choices else choices[0]
            _clear_error()
            return (data, False)
        _remember_error("AI question response was missing scenario or choices.")
    except Exception as exc:
        logger.warning("AI question parse error (%s) - using existing question.", exc)
        _remember_error(_brief_error("AI", "Could not parse AI question response", exc))
    return (None, True)
