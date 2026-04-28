"""
matcher.py — Match a trend to the best course by keyword intersection.

Computes matching keywords via set intersection and derives a score.
No streamlit imports.
"""


def match_trend_to_course(trend: dict, courses: list) -> dict:
    """
    Match a trend to the best course by keyword overlap.

    Args:
        trend: dict with 'keywords' list
        courses: list of course dicts, each with 'keywords' list

    Returns:
        dict with keys: course, score, matching_keywords, reason
    """
    if not courses:
        return {
            "course": None,
            "score": 0,
            "matching_keywords": [],
            "reason": "No courses available for matching.",
        }

    trend_kw = set(kw.lower() for kw in trend.get("keywords", []))

    best_course = None
    best_score = 0
    best_matching = []

    for course in courses:
        course_kw = set(kw.lower() for kw in course.get("keywords", []))
        matching = sorted(trend_kw & course_kw)
        # Score formula: base 84 + up to 10 from overlap ratio → max 94%
        if trend_kw:
            score = 84 + round(len(matching) / len(trend_kw) * 10)
        else:
            score = 0

        if score > best_score:
            best_score = score
            best_course = course
            best_matching = matching

    return {
        "course": best_course,
        "score": best_score,
        "matching_keywords": best_matching,
        "reason": f"Matching keywords include: {', '.join(best_matching)}.",
    }
