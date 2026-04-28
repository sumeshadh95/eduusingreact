"""Failure handling for AI text generation."""

import logging

from services.ai_errors import brief_error, remember_error

logger = logging.getLogger(__name__)


def remember_generation_failure(provider: str, error: Exception) -> None:
    provider_name = "Gemini" if provider == "gemini" else "OpenAI"
    logger.warning("%s generation failed (%s) - using fallback.", provider_name, error)
    remember_error(brief_error(provider_name, f"{provider_name} generation failed", error))
