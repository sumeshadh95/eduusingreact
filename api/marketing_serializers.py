"""Marketing payload serializers."""

from typing import Any


def camel_marketing(content: dict[str, Any], used_fallback: bool = False) -> dict[str, Any]:
    return {
        "website": content.get("website", ""),
        "social": content.get("social", ""),
        "email": content.get("email", ""),
        "tagline": content.get("tagline", ""),
        "sellingPoints": content.get("selling_points", content.get("sellingPoints", [])),
        "usedFallback": used_fallback,
    }


def snake_marketing(content: dict[str, Any]) -> dict[str, Any]:
    return {
        "website": content.get("website", ""),
        "social": content.get("social", ""),
        "email": content.get("email", ""),
        "tagline": content.get("tagline", ""),
        "selling_points": content.get("selling_points", content.get("sellingPoints", [])),
    }
