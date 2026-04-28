"""
finance.py — Income estimation formulas.

Pure math helper.
"""

import math


def compute(students: int, price: float, costs: float) -> dict:
    """
    Compute revenue, profit, and break-even figures.

    Args:
        students: expected number of students
        price: price per student (EUR)
        costs: estimated total costs (EUR)

    Returns:
        dict with revenue, profit, break_even_price, break_even_students
    """
    revenue = students * price
    profit = revenue - costs
    break_even_price = costs / students if students > 0 else 0
    break_even_students = math.ceil(costs / price) if price > 0 else 0

    return {
        "revenue": revenue,
        "profit": profit,
        "break_even_price": break_even_price,
        "break_even_students": break_even_students,
    }
