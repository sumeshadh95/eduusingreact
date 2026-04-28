"""AI course-material summarization."""

import logging

from services.ai_core import FALLBACK_SUMMARY, _generate_text

logger = logging.getLogger(__name__)


def summarize(text: str, api_key: str = None) -> tuple:
    summary = _generate_text(
        (
            "You are a helpful academic assistant. Summarize the following "
            "course material in one concise paragraph (3-5 sentences). Focus "
            "on what the student will learn and the key topics covered."
        ),
        text,
        max_tokens=300,
        temperature=0.5,
        api_key=api_key,
    )
    if summary:
        return (summary, False)
    logger.info("AI summary unavailable - using fallback summary.")
    return (FALLBACK_SUMMARY, True)
