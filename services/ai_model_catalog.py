"""Configured and fallback AI model candidates."""

from services.ai_env import env, unique_model_candidates

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def gemini_model_candidates(model: str) -> list[str]:
    return unique_model_candidates(
        [
            model,
            env("GEMINI_FALLBACK_MODEL"),
            DEFAULT_GEMINI_MODEL,
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
