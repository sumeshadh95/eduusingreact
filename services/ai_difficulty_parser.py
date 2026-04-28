"""Parse AI difficulty analysis responses."""

import logging

from services.ai_core import _brief_error, _clear_error, _parse_json_response, _remember_error
from services.ai_difficulty_fallback import fallback_difficulty

logger = logging.getLogger(__name__)


def parse_difficulty(raw: str) -> tuple:
    try:
        data = normalized_difficulty(_parse_json_response(raw))
        _clear_error()
        return (data, False)
    except Exception as exc:
        logger.warning("AI difficulty parse error (%s) - using fallback.", exc)
        _remember_error(_brief_error("AI", "Could not parse AI difficulty response", exc))
        return (fallback_difficulty(), True)


def normalized_difficulty(data: dict) -> dict:
    return {
        **data,
        "level": normalized_level(data.get("level", "Medium")),
        "rationale": data.get("rationale") or "The course has a balanced mix of theory and applied tasks.",
        "signals": data.get("signals") or [],
    }


def normalized_level(level: str) -> str:
    value = str(level or "Medium").strip().title()
    return value if value in {"Easy", "Medium", "Hard"} else "Medium"
