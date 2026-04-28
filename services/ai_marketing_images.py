"""AI marketing image generation."""

from services.ai_marketing_image_models import generate_with_gemini_models, generate_with_imagen_models
from services.ai_marketing_image_prompts import marketing_image_prompt
from services.ai_marketing_image_provider import gemini_key
from services.ai_marketing_image_results import image_failure, image_success


def generate_marketing_image(
    programme_title: str,
    content: dict,
    image_type: str,
    api_key: str = None,
) -> tuple:
    key = gemini_key(api_key)
    if not key:
        return (None, None, True)
    prompt, aspect_ratio = marketing_image_prompt(programme_title, content, image_type)
    imagen_result = generate_with_imagen_models(prompt, key, aspect_ratio)
    if imagen_result["image"]:
        return image_success(imagen_result)
    gemini_result = generate_with_gemini_models(prompt, key)
    return image_success(gemini_result) if gemini_result["image"] else image_failure(gemini_result, imagen_result)
