"""AI provider and model selection facade."""

from services.ai_env import env
from services.ai_model_catalog import (
    DEFAULT_GEMINI_MODEL,
    gemini_image_model_candidates,
    gemini_model_candidates,
    imagen_model_candidates,
)
from services.ai_provider_selection import (
    GEMINI_ALIASES,
    first_available_provider,
    requested_provider_config,
    supplied_key_config,
)


def default_gemini_model() -> str:
    return DEFAULT_GEMINI_MODEL


def get_provider_config(api_key: str = None) -> tuple:
    requested = env("AI_PROVIDER").lower()
    supplied_key = (api_key or "").strip()
    if supplied_key:
        return supplied_key_config(requested, supplied_key)
    return environment_provider_config(requested)


def environment_provider_config(requested: str) -> tuple:
    gemini_key = env("GEMINI_API_KEY") or env("GOOGLE_API_KEY")
    openai_key = env("OPENAI_API_KEY")
    if requested in GEMINI_ALIASES:
        return requested_provider_config("gemini", gemini_key)
    if requested == "openai":
        return requested_provider_config("openai", openai_key)
    return first_available_provider(gemini_key, openai_key)


def get_active_provider_name(api_key: str = None) -> str:
    provider, _, _ = get_provider_config(api_key)
    return {"gemini": "Gemini", "openai": "OpenAI"}.get(provider, "AI")
