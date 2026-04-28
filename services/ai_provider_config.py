"""AI provider and model selection."""

import os

from services.ai_errors import remember_error


def env(name: str) -> str:
    return os.environ.get(name, "").strip()


def default_gemini_model() -> str:
    return "gemini-2.0-flash"


def unique_model_candidates(candidates: list[str]) -> list[str]:
    unique = []
    for candidate in candidates:
        normalized = normalize_model_name(candidate)
        if normalized and normalized not in unique:
            unique.append(normalized)
    return unique


def normalize_model_name(model: str) -> str:
    candidate = (model or "").strip()
    if candidate.startswith("models/"):
        return candidate.split("/", 1)[1]
    return candidate


def gemini_model_candidates(model: str) -> list[str]:
    return unique_model_candidates(
        [
            model,
            env("GEMINI_FALLBACK_MODEL"),
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-flash-lite-latest",
        ]
    )


def gemini_image_model_candidates() -> list[str]:
    return unique_model_candidates(
        [
            env("GEMINI_IMAGE_MODEL"),
            "gemini-3-pro-image-preview",
            "nano-banana-pro-preview",
            "gemini-3.1-flash-image-preview",
            "gemini-2.5-flash-image",
        ]
    )


def imagen_model_candidates() -> list[str]:
    return unique_model_candidates(
        [
            env("GEMINI_IMAGEN_MODEL"),
            "imagen-4.0-generate-001",
            "imagen-4.0-fast-generate-001",
            "imagen-4.0-ultra-generate-001",
        ]
    )


def get_provider_config(api_key: str = None) -> tuple:
    requested = env("AI_PROVIDER").lower()
    supplied_key = (api_key or "").strip()
    if supplied_key:
        return provider_from_supplied_key(requested, supplied_key)

    gemini_key = env("GEMINI_API_KEY") or env("GOOGLE_API_KEY")
    openai_key = env("OPENAI_API_KEY")
    if requested in {"gemini", "google"}:
        return requested_provider("gemini", gemini_key)
    if requested == "openai":
        return requested_provider("openai", openai_key)
    return first_available_provider(gemini_key, openai_key)


def provider_from_supplied_key(requested: str, supplied_key: str) -> tuple:
    use_gemini = (
        requested in {"gemini", "google"}
        or supplied_key.startswith("AIza")
        or supplied_key == env("GEMINI_API_KEY")
        or supplied_key == env("GOOGLE_API_KEY")
    )
    if use_gemini:
        return ("gemini", supplied_key, env("GEMINI_MODEL") or default_gemini_model())
    return ("openai", supplied_key, env("OPENAI_MODEL") or "gpt-4o-mini")


def requested_provider(provider: str, key: str) -> tuple:
    if not key:
        remember_error(f"No {provider_api_key_name(provider)} was found. Add it to .env and try again.")
        return (None, None, None)
    if provider == "gemini":
        return ("gemini", key, env("GEMINI_MODEL") or default_gemini_model())
    return ("openai", key, env("OPENAI_MODEL") or "gpt-4o-mini")


def first_available_provider(gemini_key: str, openai_key: str) -> tuple:
    if gemini_key:
        return ("gemini", gemini_key, env("GEMINI_MODEL") or default_gemini_model())
    if openai_key:
        return ("openai", openai_key, env("OPENAI_MODEL") or "gpt-4o-mini")
    remember_error("No AI API key was found. Add GEMINI_API_KEY or OPENAI_API_KEY to .env.")
    return (None, None, None)


def provider_api_key_name(provider: str) -> str:
    return "GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY"


def get_active_provider_name(api_key: str = None) -> str:
    provider, _, _ = get_provider_config(api_key)
    return {"gemini": "Gemini", "openai": "OpenAI"}.get(provider, "AI")
