"""Provider config tuple builders."""

from services.ai_env import env
from services.ai_model_catalog import DEFAULT_GEMINI_MODEL, DEFAULT_OPENAI_MODEL

MODEL_DEFAULTS = {
    "gemini": ("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
    "openai": ("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
}


def provider_config(provider: str, key: str) -> tuple:
    model_env, default_model = MODEL_DEFAULTS[provider]
    return (provider, key, env(model_env) or default_model)


def api_key_name(provider: str) -> str:
    return "GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY"
