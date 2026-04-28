"""Bootstrap payload for the React app."""

from api.config import provider_status
from services import data_loader


def bootstrap_payload() -> dict:
    return {
        "trends": data_loader.load_trends(),
        "courses": data_loader.load_courses(),
        "teachers": data_loader.load_teachers(),
        "provider": provider_status(),
    }


def selected_trend(trend_name: str) -> dict | None:
    return next((item for item in data_loader.load_trends() if item.get("trend") == trend_name), None)
