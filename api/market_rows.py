"""Market comparison row helpers."""

from typing import Any


def dominant_demand(similar_courses: list[dict[str, Any]]) -> str:
    demand_counts: dict[str, int] = {}
    for item in similar_courses:
        demand = item.get("demand", "Medium")
        demand_counts[demand] = demand_counts.get(demand, 0) + 1
    return max(demand_counts, key=demand_counts.get) if demand_counts else "Medium"


def comparison_rows(similar_courses: list[dict[str, Any]], xamk_price: int) -> list[dict[str, Any]]:
    return [
        {
            "provider": item.get("provider", ""),
            "title": item.get("title", ""),
            "platformPrice": item.get("price_eur", 0),
            "xamkPrice": xamk_price,
            "difference": item.get("price_eur", 0) - xamk_price,
            "format": item.get("format", ""),
            "demand": item.get("demand", ""),
        }
        for item in similar_courses
    ]
