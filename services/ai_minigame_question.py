"""AI mini-game question regeneration."""

import logging

from services.ai_core import _generate_text
from services.ai_json_validation import parse_validated_json

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
    return parse_validated_json(
        raw,
        validator=normalize_minigame_question,
        success_message="AI mini-game question generated successfully.",
        missing_message="AI question response was missing scenario or choices.",
        parse_prefix="Could not parse AI question response",
        warning_template="AI question parse error (%s) - using existing question.",
        logger=logger,
    )


def normalize_minigame_question(data: dict) -> bool:
    choices = data.get("choices", [])
    if not data.get("scenario") or len(choices) < 2:
        return False
    data["correct_choice"] = data.get("correct_choice") if data.get("correct_choice") in choices else choices[0]
    return True
