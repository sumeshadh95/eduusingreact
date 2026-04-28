"""Model-attempt loop for marketing image generation."""

import logging

from services.ai_image_errors import is_image_access_error
from services.ai_retry import retry_call

logger = logging.getLogger(__name__)


def try_models(models: list, generate_image, attempts: int, provider_name: str) -> dict:
    result = empty_result()
    for model in models:
        model_result = try_model(model, generate_image, attempts)
        result = merge_results(result, model_result)
        if model_result["image"]:
            logger.info("%s image generated with %s.", provider_name, model)
            return model_result
    return result


def try_model(model: str, generate_image, attempts: int) -> dict:
    image_result, error = retry_call(lambda: generate_image(model), attempts)
    if image_result:
        image_bytes, mime_type = image_result
        return {"image": image_bytes, "mime": mime_type, "error": None, "access_error": None}
    return {"image": None, "mime": None, "error": error, "access_error": access_error(error)}


def empty_result() -> dict:
    return {"image": None, "mime": None, "error": None, "access_error": None}


def merge_results(current: dict, latest: dict) -> dict:
    return {
        "image": latest["image"] or current["image"],
        "mime": latest["mime"] or current["mime"],
        "error": latest["error"] or current["error"],
        "access_error": latest["access_error"] or current["access_error"],
    }


def access_error(error: Exception) -> Exception | None:
    return error if error and is_image_access_error(error) else None
