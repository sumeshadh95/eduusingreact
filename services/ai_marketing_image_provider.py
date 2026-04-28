"""Provider validation for marketing-image generation."""

from services.ai_core import _get_provider_config, _remember_error


def gemini_key(api_key: str = None) -> str | None:
    provider, key, _ = _get_provider_config(api_key)
    if provider == "gemini" and key:
        return key
    _remember_error("Gemini image generation requires GEMINI_API_KEY in .env.")
    return None
