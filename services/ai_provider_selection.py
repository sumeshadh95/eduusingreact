"""Provider selection rules for Gemini and OpenAI."""

from services.ai_errors import remember_error
from services.ai_provider_detection import GEMINI_ALIASES, first_available_key, supplied_key_provider
from services.ai_provider_records import api_key_name, provider_config


def supplied_key_config(requested: str, supplied_key: str) -> tuple:
    return provider_config(supplied_key_provider(requested, supplied_key), supplied_key)


def requested_provider_config(provider: str, key: str) -> tuple:
    if not key:
        remember_error(f"No {api_key_name(provider)} was found. Add it to .env and try again.")
        return (None, None, None)
    return provider_config(provider, key)


def first_available_provider(gemini_key: str, openai_key: str) -> tuple:
    provider_key = first_available_key(gemini_key, openai_key)
    if provider_key:
        provider, key = provider_key
        return provider_config(provider, key)
    remember_error("No AI API key was found. Add GEMINI_API_KEY or OPENAI_API_KEY to .env.")
    return (None, None, None)
