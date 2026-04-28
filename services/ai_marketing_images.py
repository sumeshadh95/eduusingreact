"""AI marketing image generation."""

import logging

from services.ai_core import (
    _brief_error,
    _clear_error,
    _generate_image_with_gemini,
    _generate_image_with_imagen,
    _gemini_image_model_candidates,
    _get_provider_config,
    _imagen_model_candidates,
    _remember_error,
)
from services.ai_image_attempts import try_models
from services.ai_marketing_image_prompts import marketing_image_prompt

logger = logging.getLogger(__name__)


def generate_marketing_image(
    programme_title: str,
    content: dict,
    image_type: str,
    api_key: str = None,
) -> tuple:
    provider, key, _ = _get_provider_config(api_key)
    if provider != "gemini" or not key:
        _remember_error("Gemini image generation requires GEMINI_API_KEY in .env.")
        return (None, None, True)

    prompt, aspect_ratio = marketing_image_prompt(programme_title, content, image_type)
    imagen_result = generate_with_imagen_models(prompt, key, aspect_ratio)
    if imagen_result["image"]:
        return image_success(imagen_result)
    gemini_result = generate_with_gemini_models(prompt, key)
    if gemini_result["image"]:
        return image_success(gemini_result)
    return image_failure(gemini_result, imagen_result)


def generate_with_imagen_models(prompt: str, key: str, aspect_ratio: str) -> dict:
    return try_models(
        _imagen_model_candidates(),
        lambda model: _generate_image_with_imagen(prompt, api_key=key, model=model, aspect_ratio=aspect_ratio),
        attempts=2,
        provider_name="Imagen",
    )


def generate_with_gemini_models(prompt: str, key: str) -> dict:
    return try_models(
        _gemini_image_model_candidates(),
        lambda model: _generate_image_with_gemini(prompt, api_key=key, model=model),
        attempts=3,
        provider_name="Gemini",
    )


def image_success(result: dict) -> tuple:
    _clear_error()
    return (result["image"], result["mime"], False)


def image_failure(gemini_result: dict, imagen_result: dict) -> tuple:
    final_error = (
        gemini_result.get("access_error")
        or imagen_result.get("access_error")
        or gemini_result.get("error")
        or imagen_result.get("error")
    )
    _remember_error(_brief_error("Gemini", "Gemini image generation failed", final_error))
    logger.warning("Gemini image generation failed (%s).", final_error)
    return (None, None, True)
