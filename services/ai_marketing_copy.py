"""AI marketing copy generation."""

import logging

from services.ai_core import _brief_error, _clear_error, _generate_text, _parse_json_response, _remember_error

logger = logging.getLogger(__name__)


def generate_marketing_content(
    programme_title: str, course_name: str, weeks: int, ects: int, api_key: str = None
) -> tuple:
    raw = _generate_text(
        "You are an expert university marketing copywriter. Always respond with valid JSON only.",
        marketing_prompt(programme_title, course_name, weeks, ects),
        max_tokens=1500,
        temperature=0.7,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)
    return parse_marketing_content(raw)


def marketing_prompt(programme_title: str, course_name: str, weeks: int, ects: int) -> str:
    return f"""Generate marketing content for a university short programme called "{programme_title}" based on the course "{course_name}". It is a {weeks}-week, {ects} ECTS online programme by Xamk university.

Return ONLY valid JSON with this exact structure, no markdown:
{{
  "website": "A compelling website description (3-4 sentences) for the programme page.",
  "social": "A social media post with emojis and hashtags promoting the programme.",
  "email": "A professional partner school email (Dear Partner format) announcing the programme.",
  "tagline": "A catchy one-line tagline for the programme.",
  "selling_points": [
    "First selling point (1-2 sentences about industry relevance).",
    "Second selling point (1-2 sentences about accessibility).",
    "Third selling point (1-2 sentences about flexibility and credits)."
  ]
}}"""


def parse_marketing_content(raw: str) -> tuple:
    try:
        data = _parse_json_response(raw)
        if "website" in data and "selling_points" in data:
            logger.info("AI marketing content generated successfully.")
            _clear_error()
            return (data, False)
        _remember_error("AI marketing response was missing required fields.")
    except Exception as exc:
        logger.warning("AI marketing parse error (%s) - using fallback.", exc)
        _remember_error(_brief_error("AI", "Could not parse AI marketing response", exc))
    return (None, True)
