"""Compatibility facade for Gemini and Imagen image clients."""

from services.ai_gemini_image_client import generate_image_with_gemini
from services.ai_image_extractors import is_image_access_error
from services.ai_imagen_client import generate_image_with_imagen

__all__ = [
    "generate_image_with_gemini",
    "generate_image_with_imagen",
    "is_image_access_error",
]
