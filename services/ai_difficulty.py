"""AI course difficulty analysis."""

from services.ai_core import _generate_text
from services.ai_difficulty_fallback import fallback_difficulty
from services.ai_difficulty_parser import parse_difficulty
from services.ai_difficulty_prompt import difficulty_prompt


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
    return parse_difficulty(raw) if raw else (fallback_difficulty(), True)
