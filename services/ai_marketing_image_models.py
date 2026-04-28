"""Provider model runners for marketing-image generation."""

from services.ai_core import (
    _generate_image_with_gemini,
    _generate_image_with_imagen,
    _gemini_image_model_candidates,
    _imagen_model_candidates,
)
from services.ai_image_attempts import try_models


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
