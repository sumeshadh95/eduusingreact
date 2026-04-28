"""Provider detection helpers."""

from services.ai_env import env

GEMINI_ALIASES = {"gemini", "google"}


def supplied_key_provider(requested: str, supplied_key: str) -> str:
    return "gemini" if supplied_key_is_gemini(requested, supplied_key) else "openai"


def supplied_key_is_gemini(requested: str, supplied_key: str) -> bool:
    return any(
        [
            requested in GEMINI_ALIASES,
            supplied_key.startswith("AIza"),
            supplied_key == env("GEMINI_API_KEY"),
            supplied_key == env("GOOGLE_API_KEY"),
        ]
    )


def first_available_key(gemini_key: str, openai_key: str) -> tuple | None:
    return next(
        ((provider, key) for provider, key in [("gemini", gemini_key), ("openai", openai_key)] if key),
        None,
    )
