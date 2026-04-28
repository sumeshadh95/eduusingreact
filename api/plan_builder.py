"""Build the full CoursePilot plan payload consumed by the React UI."""

from typing import Any

from api.config import effective_api_key
from api.plan_ai_results import plan_ai_results
from api.plan_context import find_teacher, plan_context
from api.plan_payload import match_payload, plan_payload
from api.plan_programme import fallback_programme, generate_marketing, generate_programme


def build_plan(trend: dict[str, Any]) -> dict[str, Any]:
    context = plan_context(trend)
    generated = plan_ai_results(context, effective_api_key())
    return plan_payload(context, generated)


__all__ = [
    "build_plan",
    "fallback_programme",
    "find_teacher",
    "generate_marketing",
    "generate_programme",
    "match_payload",
]
