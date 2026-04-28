"""Run a single image model with retries."""

from services.ai_image_attempt_results import failure_result, success_result
from services.ai_retry import retry_call


def try_model(model: str, generate_image, attempts: int) -> dict:
    image_result, error = retry_call(lambda: generate_image(model), attempts)
    return success_result(image_result) if image_result else failure_result(error)
