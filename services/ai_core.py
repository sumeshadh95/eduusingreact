"""Compatibility facade for shared AI provider/client helpers."""

from services.ai_errors import (
    FALLBACK_SUMMARY,
    brief_error as _brief_error,
    clear_error as _clear_error,
    get_last_error,
    remember_error as _remember_error,
)
from services.ai_image_client import (
    generate_image_with_gemini as _generate_image_with_gemini,
    generate_image_with_imagen as _generate_image_with_imagen,
    is_image_access_error as _is_image_access_error,
)
from services.ai_provider_config import (
    gemini_image_model_candidates as _gemini_image_model_candidates,
    get_active_provider_name,
    get_provider_config as _get_provider_config,
    imagen_model_candidates as _imagen_model_candidates,
)
from services.ai_text_client import (
    generate_text as _generate_text,
    parse_json_response as _parse_json_response,
)

__all__ = [
    "FALLBACK_SUMMARY",
    "_brief_error",
    "_clear_error",
    "_generate_image_with_gemini",
    "_generate_image_with_imagen",
    "_generate_text",
    "_gemini_image_model_candidates",
    "_get_provider_config",
    "_imagen_model_candidates",
    "_is_image_access_error",
    "_parse_json_response",
    "_remember_error",
    "get_active_provider_name",
    "get_last_error",
]
