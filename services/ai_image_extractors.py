"""Compatibility facade for image response extraction."""

from services.ai_image_errors import is_image_access_error
from services.ai_imagen_parser import extract_imagen_prediction
from services.ai_inline_image_parser import extract_inline_image

__all__ = [
    "extract_image_prediction",
    "extract_imagen_prediction",
    "extract_inline_image",
    "is_image_access_error",
]

extract_image_prediction = extract_imagen_prediction
