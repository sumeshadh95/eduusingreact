"""Fallback model retry loop for Gemini text generation."""

import logging

from services.ai_model_catalog import gemini_model_candidates
from services.ai_retry import retry_call

logger = logging.getLogger(__name__)


def generate_with_gemini_fallbacks(
    generate_for_model,
    configured_model: str,
) -> str:
    last_error = None
    for candidate_model in gemini_model_candidates(configured_model):
        text, last_error = retry_call(lambda: generate_for_model(candidate_model), attempts=3)
        if text:
            log_success(candidate_model, configured_model)
            return text
    raise last_error or RuntimeError("Gemini generation failed.")


def log_success(candidate_model: str, configured_model: str) -> None:
    if candidate_model != configured_model:
        logger.info("Gemini generation used fallback model %s.", candidate_model)
    logger.info("Gemini generation completed successfully.")
