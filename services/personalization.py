"""Personalized learning content with AI first and local fallback data."""

import json
from functools import lru_cache
from pathlib import Path

from services import ai_service

FALLBACK_PATH = Path(__file__).resolve().parents[1] / "data" / "personalization_fallback.json"


def get_personalized_chapters(course_name: str, student_field: str, api_key: str = None) -> tuple:
    data, used_fallback = ai_service.generate_personalized_chapters(
        course_name, student_field, api_key
    )
    if not used_fallback and data:
        return (
            data.get("chapters", []),
            data.get("final_assignment", get_final_assignment()),
            False,
        )
    return (get_nursing_chapters(), get_final_assignment(), True)


def fallback_personalization() -> dict:
    return _fallback_personalization()


@lru_cache(maxsize=1)
def _fallback_personalization() -> dict:
    try:
        return json.loads(FALLBACK_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"chapters": [], "final_assignment": ""}


def get_nursing_chapters() -> list:
    return fallback_personalization().get("chapters", [])


def get_final_assignment() -> str:
    return fallback_personalization().get("final_assignment", "")
