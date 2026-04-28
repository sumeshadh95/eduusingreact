"""Mock market analysis used for CoursePilot price recommendations."""

from typing import Any

from api.market_data import find_market_entry
from api.market_pricing import course_prices, percent_saving, price_range, recommended_price
from api.market_rows import comparison_rows, dominant_demand


def market_analysis(course: dict[str, Any], trend: dict[str, Any]) -> dict[str, Any]:
    similar_courses = find_market_entry(course, trend).get("courses", [])
    average_price, price, difference = recommended_price(course_prices(similar_courses))
    recommended_range = price_range(price)
    return {
        "similarCourses": similar_courses,
        "averageCompetitorPrice": average_price,
        "recommendedPrice": price,
        "recommendedRange": recommended_range,
        "priceDifference": difference,
        "percentSaving": percent_saving(difference, average_price),
        "demandLabel": dominant_demand(similar_courses),
        "positioning": positioning_copy(average_price, recommended_range),
        "comparisonRows": comparison_rows(similar_courses, price),
    }


def positioning_copy(average_price: int, recommended_range: dict[str, int]) -> str:
    return (
        f"Comparable programmes cluster around EUR {average_price}. "
        f"A Xamk price near EUR {recommended_range['low']}-{recommended_range['high']} "
        "undercuts the market while preserving a premium academic signal."
    )
