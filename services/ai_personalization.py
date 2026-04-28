
"""ai_personalization.py - AI personalized chapters and mini-game questions."""

import json
import logging

from services.ai_core import (
    _brief_error,
    _clear_error,
    _generate_text,
    _parse_json_response,
    _remember_error,
)

logger = logging.getLogger(__name__)

def generate_personalized_chapters(
    course_name: str, student_field: str, api_key: str = None
) -> tuple:
    """
    Generate personalized learning chapters using the configured AI provider.

    Returns:
        tuple of (data: dict with 'chapters' and 'final_assignment', used_fallback: bool)
    """
    prompt = f"""Create 5 learning chapters for a course called "{course_name}" personalized for a {student_field} student.

For each chapter, provide:
1. A chapter title relevant to the course content
2. A standard explanation (2-3 sentences) of what this chapter covers
3. A personalized explanation (2-3 sentences) showing how this chapter's topic connects to the {student_field} field specifically
4. A simple playable mini-game concept that helps {student_field} students learn through gamification. Each game must include a scenario, four choices, the correct choice text, and feedback.

Also provide a final assignment description (3-4 sentences) that bridges {course_name} with {student_field}.

Return ONLY valid JSON with this exact structure, no markdown formatting:
{{
  "chapters": [
    {{
      "title": "Chapter 1 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }},
    {{
      "title": "Chapter 2 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }},
    {{
      "title": "Chapter 3 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }},
    {{
      "title": "Chapter 4 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }},
    {{
      "title": "Chapter 5 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }}
  ],
  "final_assignment": "..."
}}

Make the content educational, creative, and specifically relevant to how {student_field} students can benefit from learning {course_name}."""

    raw = _generate_text(
        "You are an expert educational content designer. Always respond with valid JSON only.",
        prompt,
        max_tokens=2000,
        temperature=0.7,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        if "chapters" in data and len(data["chapters"]) >= 5:
            logger.info("AI personalized chapters generated successfully.")
            _clear_error()
            return (data, False)
        _remember_error("AI personalization response was missing chapters.")
        return (None, True)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.warning("Failed to parse AI personalization response (%s) - using fallback.", e)
        _remember_error(_brief_error("AI", "Could not parse AI personalization response", e))
        return (None, True)


def generate_minigame_question(
    course_name: str,
    student_field: str,
    chapter: dict,
    api_key: str = None,
) -> tuple:
    """
    Generate one editable mini-game question for a chapter.

    Returns:
        tuple of (minigame: dict, used_fallback: bool)
    """
    prompt = f"""Generate one simple playable mini-game question for this learning chapter.

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

    raw = _generate_text(
        "You are an educational game designer. Always respond with valid JSON only.",
        prompt,
        max_tokens=900,
        temperature=0.75,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        choices = data.get("choices", [])
        correct = data.get("correct_choice", "")
        if data.get("scenario") and len(choices) >= 2:
            if correct not in choices:
                data["correct_choice"] = choices[0]
            _clear_error()
            return (data, False)
        _remember_error("AI question response was missing scenario or choices.")
        return (None, True)
    except Exception as e:
        logger.warning("AI question parse error (%s) - using existing question.", e)
        _remember_error(_brief_error("AI", "Could not parse AI question response", e))
        return (None, True)


def generate_chapter_text_patch(
    course_name: str,
    student_field: str,
    chapter: dict,
    api_key: str = None,
) -> tuple:
    """
    Generate missing chapter title/explanation copy without changing the game.

    Returns:
        tuple of (chapter_text: dict, used_fallback: bool)
    """
    game = chapter.get("minigame", {}) or {}
    prompt = f"""Write polished chapter text for an admin-edited personalized learning module.

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

    raw = _generate_text(
        "You are an expert instructional designer. Always respond with valid JSON only.",
        prompt,
        max_tokens=850,
        temperature=0.65,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        required = ["title", "standard_explanation", "personalized_explanation"]
        if all(str(data.get(key, "")).strip() for key in required):
            _clear_error()
            return (data, False)
        _remember_error("AI chapter text response was missing title or explanations.")
        return (None, True)
    except Exception as e:
        logger.warning("AI chapter text parse error (%s).", e)
        _remember_error(_brief_error("AI", "Could not parse AI chapter text response", e))
        return (None, True)


