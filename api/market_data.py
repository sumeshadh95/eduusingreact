"""Market mock-data loading and lookup."""

import json
from typing import Any

from api.config import BASE_DIR


def load_market_courses() -> list[dict[str, Any]]:
    path = BASE_DIR / "data" / "market_courses.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def find_market_entry(course: dict[str, Any], trend: dict[str, Any]) -> dict[str, Any]:
    return next((item for item in load_market_courses() if market_entry_matches(item, course, trend)), {})


def market_entry_matches(item: dict[str, Any], course: dict[str, Any], trend: dict[str, Any]) -> bool:
    return item.get("course_id") == course.get("course_id") or item.get("trend", "").lower() == trend.get(
        "trend", ""
    ).lower()
