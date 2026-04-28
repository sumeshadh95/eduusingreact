"""AI personalized chapter generation."""

import json
import logging

from services.ai_core import _brief_error, _clear_error, _generate_text, _parse_json_response, _remember_error

logger = logging.getLogger(__name__)


def generate_personalized_chapters(
    course_name: str, student_field: str, api_key: str = None
) -> tuple:
    raw = _generate_text(
        "You are an expert educational content designer. Always respond with valid JSON only.",
        personalized_chapters_prompt(course_name, student_field),
        max_tokens=2000,
        temperature=0.7,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)
    return parse_personalized_chapters(raw)


def personalized_chapters_prompt(course_name: str, student_field: str) -> str:
    return f"""Create 5 learning chapters for a course called "{course_name}" personalized for a {student_field} student.

For each chapter, provide a title, a standard explanation, a personalized explanation connecting the topic to {student_field}, and a simple playable mini-game concept. Each game must include a scenario, four choices, the correct choice text, and feedback.

Also provide a final assignment description that bridges {course_name} with {student_field}.

Return ONLY valid JSON with this exact structure, no markdown formatting:
{{
  "chapters": [
    {{
      "title": "Chapter 1 - [Title]",
      "standard_explanation": "2-3 sentences",
      "personalized_explanation": "2-3 sentences",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "One-sentence game description",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }}
  ],
  "final_assignment": "3-4 sentences"
}}

Make the content educational, creative, and specifically relevant to how {student_field} students can benefit from learning {course_name}."""


def parse_personalized_chapters(raw: str) -> tuple:
    try:
        data = _parse_json_response(raw)
        if "chapters" in data and len(data["chapters"]) >= 5:
            logger.info("AI personalized chapters generated successfully.")
            _clear_error()
            return (data, False)
        _remember_error("AI personalization response was missing chapters.")
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        logger.warning("Failed to parse AI personalization response (%s) - using fallback.", exc)
        _remember_error(_brief_error("AI", "Could not parse AI personalization response", exc))
    return (None, True)
