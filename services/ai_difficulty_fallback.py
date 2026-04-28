"""Fallback difficulty classification."""

FALLBACK_DIFFICULTY = {
    "level": "Medium",
    "rationale": "The course combines beginner concepts with practical tool-based project work.",
    "signals": ["Beginner-facing source course", "Hands-on project work", "Guided short programme format"],
}


def fallback_difficulty() -> dict:
    return dict(FALLBACK_DIFFICULTY)
