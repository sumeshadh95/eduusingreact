"""Compatibility facade for AI personalization helpers."""

from services.ai_chapter_text import generate_chapter_text_patch
from services.ai_minigame_question import generate_minigame_question
from services.ai_personalized_chapters import generate_personalized_chapters

__all__ = [
    "generate_chapter_text_patch",
    "generate_minigame_question",
    "generate_personalized_chapters",
]
