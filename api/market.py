"""Mock market analysis used for CoursePilot price recommendations."""

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
    for item in load_market_courses():
        if item.get("course_id") == course.get("course_id"):
            return item
        if item.get("trend", "").lower() == trend.get("trend", "").lower():
            return item
    return {}


def recommended_price(prices: list[float]) -> tuple[int, int, int]:
    average_price = round(sum(prices) / len(prices)) if prices else 400
    price = round((average_price * 0.775) / 5) * 5
    price = min(max(price, 250), max(250, average_price - 50))
    return (average_price, price, average_price - price)


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


def market_analysis(course: dict[str, Any], trend: dict[str, Any]) -> dict[str, Any]:
    similar_courses = find_market_entry(course, trend).get("courses", [])
    prices = [float(item.get("price_eur", 0)) for item in similar_courses if item.get("price_eur")]
    average_price, price, difference = recommended_price(prices)
    range_low = max(199, price - 10)
    range_high = price + 5
    percent_saving = round((difference / average_price) * 100) if average_price else 0

    return {
        "similarCourses": similar_courses,
        "averageCompetitorPrice": average_price,
        "recommendedPrice": price,
        "recommendedRange": {"low": range_low, "high": range_high},
        "priceDifference": difference,
        "percentSaving": percent_saving,
        "demandLabel": dominant_demand(similar_courses),
        "positioning": positioning_copy(average_price, range_low, range_high),
        "comparisonRows": comparison_rows(similar_courses, price),
    }


def positioning_copy(average_price: int, range_low: int, range_high: int) -> str:
    return (
        f"Comparable programmes cluster around EUR {average_price}. "
        f"A Xamk price near EUR {range_low}-{range_high} undercuts the market while preserving a premium academic signal."
    )
