"""Result helpers for marketing-image generation."""

import logging

from services.ai_core import _brief_error, _clear_error, _remember_error

logger = logging.getLogger(__name__)


def image_success(result: dict) -> tuple:
    _clear_error()
    return (result["image"], result["mime"], False)


def image_failure(gemini_result: dict, imagen_result: dict) -> tuple:
    final_error = selected_error(gemini_result, imagen_result)
    _remember_error(_brief_error("Gemini", "Gemini image generation failed", final_error))
    logger.warning("Gemini image generation failed (%s).", final_error)
    return (None, None, True)


def selected_error(gemini_result: dict, imagen_result: dict):
    return (
        gemini_result.get("access_error")
        or imagen_result.get("access_error")
        or gemini_result.get("error")
        or imagen_result.get("error")
    )
