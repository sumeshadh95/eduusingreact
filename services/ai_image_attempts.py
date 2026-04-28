"""Model-attempt loop for marketing image generation."""

import logging
from functools import reduce

from services.ai_image_attempt_results import empty_result, merge_results
from services.ai_image_single_attempt import try_model

logger = logging.getLogger(__name__)


def try_models(models: list, generate_image, attempts: int, provider_name: str) -> dict:
    results = [(model, try_model(model, generate_image, attempts)) for model in models]
    successful = next(((model, result) for model, result in results if result["image"]), None)
    if successful:
        model, result = successful
        logger.info("%s image generated with %s.", provider_name, model)
        return result
    return reduce(lambda current, pair: merge_results(current, pair[1]), results, empty_result())
