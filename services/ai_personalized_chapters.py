"""AI personalized chapter generation."""

import json
import logging

from services.ai_core import _generate_text
from services.ai_json_validation import parse_validated_json

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
    return parse_validated_json(
        raw,
        validator=has_personalized_chapters,
        success_message="AI personalized chapters generated successfully.",
        missing_message="AI personalization response was missing chapters.",
        parse_prefix="Could not parse AI personalization response",
        warning_template="Failed to parse AI personalization response (%s) - using fallback.",
        logger=logger,
        exceptions=(json.JSONDecodeError, KeyError, IndexError),
    )


def has_personalized_chapters(data: dict) -> bool:
    return "chapters" in data and len(data["chapters"]) >= 5
