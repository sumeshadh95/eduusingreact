"""Compatibility facade for AI curriculum helpers."""

from services.ai_difficulty import analyze_course_difficulty
from services.ai_programme_content import generate_programme_content
from services.ai_summary import summarize

__all__ = ["analyze_course_difficulty", "generate_programme_content", "summarize"]
