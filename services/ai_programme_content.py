"""AI short-programme content generation."""

from services.ai_core import _generate_text
from services.ai_programme_parser import parse_programme
from services.ai_programme_prompt import programme_prompt


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
