"""
material_analyzer.py — Analyze course material word count to determine
size bucket and recommended duration.

Buckets:
  <200 words   → Small,      1 week
  200–800      → Medium,     2 weeks
  800–1500     → Large,      3 weeks
  >1500        → Very Large, 4 weeks

ECTS is always 3.
"""


def analyze(text: str) -> dict:
    """
    Analyze material text and return size/duration/ects metadata.

    Args:
        text: the raw course material text

    Returns:
        dict with keys: size, weeks, ects, word_count
    """
    word_count = len(text.split()) if text else 0

    if word_count < 200:
        size = "Small"
        weeks = 1
    elif word_count <= 800:
        size = "Medium"
        weeks = 2
    elif word_count <= 1500:
        size = "Large"
        weeks = 3
    else:
        size = "Very Large"
        weeks = 4

    return {
        "size": size,
        "weeks": weeks,
        "ects": 3,
        "word_count": word_count,
    }
