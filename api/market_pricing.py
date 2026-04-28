"""Market pricing calculations."""

from typing import Any


def recommended_price(prices: list[float]) -> tuple[int, int, int]:
    average_price = round(sum(prices) / len(prices)) if prices else 400
    price = round((average_price * 0.775) / 5) * 5
    price = min(max(price, 250), max(250, average_price - 50))
    return (average_price, price, average_price - price)


def course_prices(similar_courses: list[dict[str, Any]]) -> list[float]:
    return [float(item.get("price_eur", 0)) for item in similar_courses if item.get("price_eur")]


def price_range(price: int) -> dict[str, int]:
    return {"low": max(199, price - 10), "high": price + 5}


def percent_saving(difference: int, average_price: int) -> int:
    return round((difference / average_price) * 100) if average_price else 0
