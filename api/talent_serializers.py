"""Talent payload serializers."""

from typing import Any


def camel_talent(candidate: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(candidate)
    enriched["matchScore"] = candidate.get("match_score", candidate.get("matchScore", 0))
    enriched["matchReasons"] = candidate.get("match_reasons", candidate.get("matchReasons", []))
    return enriched
