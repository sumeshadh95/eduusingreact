"""AI marketing image generation."""

import logging
import time

from services.ai_core import (
    _brief_error,
    _clear_error,
    _generate_image_with_gemini,
    _generate_image_with_imagen,
    _gemini_image_model_candidates,
    _get_provider_config,
    _imagen_model_candidates,
    _is_image_access_error,
    _remember_error,
)

logger = logging.getLogger(__name__)


def generate_marketing_image(
    programme_title: str,
    content: dict,
    image_type: str,
    api_key: str = None,
) -> tuple:
    provider, key, _ = _get_provider_config(api_key)
    if provider != "gemini" or not key:
        _remember_error("Gemini image generation requires GEMINI_API_KEY in .env.")
        return (None, None, True)

    prompt, aspect_ratio = marketing_image_prompt(programme_title, content, image_type)
    imagen_result = try_models(
        _imagen_model_candidates(),
        lambda model: _generate_image_with_imagen(prompt, api_key=key, model=model, aspect_ratio=aspect_ratio),
        attempts=2,
        provider_name="Imagen",
    )
    if imagen_result["image"]:
        return image_success(imagen_result)

    gemini_result = try_models(
        _gemini_image_model_candidates(),
        lambda model: _generate_image_with_gemini(prompt, api_key=key, model=model),
        attempts=3,
        provider_name="Gemini",
    )
    if gemini_result["image"]:
        return image_success(gemini_result)
    return image_failure(gemini_result, imagen_result)


def marketing_image_prompt(programme_title: str, content: dict, image_type: str) -> tuple[str, str]:
    if image_type == "social":
        return (
            f"""Create a beautiful, polished square social media image for Xamk's short programme "{programme_title}".
Visual direction: modern university marketing, energetic game development theme, students designing prototypes with laptops and game controllers, subtle Finland/Xamk academic feel, clean composition, Xamk green and deep blue brand accents, readable space for caption overlay, no tiny unreadable text.
Tagline inspiration: {content.get("tagline", "")}
Style: professional, bright, credible, premium, demo-ready.""",
            "1:1",
        )
    return (
        f"""Create a beautiful professional brochure/pamphlet cover image for Xamk's short programme "{programme_title}".
Visual direction: A4-style cover, game development sprint theme, creative technology classroom, prototype screens, approachable university continuing education, Xamk green and deep blue brand accents, clean layout space for title and dates, no tiny unreadable text.
Website copy inspiration: {content.get("website", "")}
Style: premium university brochure, polished, credible, demo-ready.""",
        "3:4",
    )


def try_models(models: list, generate_image, attempts: int, provider_name: str) -> dict:
    result = {"image": None, "mime": None, "error": None, "access_error": None}
    for model in models:
        model_result = try_model(model, generate_image, attempts)
        result["error"] = model_result["error"] or result["error"]
        result["access_error"] = model_result["access_error"] or result["access_error"]
        if model_result["image"]:
            logger.info("%s image generated with %s.", provider_name, model)
            return model_result
    return result


def try_model(model: str, generate_image, attempts: int) -> dict:
    result = {"image": None, "mime": None, "error": None, "access_error": None}
    for attempt in range(attempts):
        try:
            image_bytes, mime_type = generate_image(model)
            result.update({"image": image_bytes, "mime": mime_type})
            return result
        except Exception as exc:
            result["error"] = exc
            result["access_error"] = result["access_error"] or (exc if _is_image_access_error(exc) else None)
            if retryable_image_error(exc) and attempt < attempts - 1:
                time.sleep(1 + attempt)
                continue
            return result
    return result


def retryable_image_error(error: Exception) -> bool:
    detail = str(error).lower()
    return any(
        marker in detail
        for marker in ["503", "high demand", "unavailable", "connection", "timeout", "temporarily"]
    )


def image_success(result: dict) -> tuple:
    _clear_error()
    return (result["image"], result["mime"], False)


def image_failure(gemini_result: dict, imagen_result: dict) -> tuple:
    final_error = (
        gemini_result.get("access_error")
        or imagen_result.get("access_error")
        or gemini_result.get("error")
        or imagen_result.get("error")
    )
    _remember_error(_brief_error("Gemini", "Gemini image generation failed", final_error))
    logger.warning("Gemini image generation failed (%s).", final_error)
    return (None, None, True)
