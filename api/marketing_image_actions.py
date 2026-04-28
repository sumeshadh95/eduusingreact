"""Marketing image route actions."""

from api.config import effective_api_key, provider_status
from api.image_assets import save_generated_image
from api.route_responses import failed_image_response
from api.serializers import snake_marketing
from services import ai_service


def generate_marketing_image_payload(programme_title: str, content: dict, image_type: str) -> dict:
    image_bytes, mime_type, used_fallback = ai_service.generate_marketing_image(
        programme_title,
        snake_marketing(content),
        image_type,
        api_key=effective_api_key(),
    )
    if not image_bytes or used_fallback:
        return failed_image_response()
    return image_success_payload(image_bytes, mime_type, image_type)


def image_success_payload(image_bytes: bytes, mime_type: str, image_type: str) -> dict:
    return {
        "ok": True,
        "imageType": image_type,
        "imageUrl": save_generated_image(image_bytes, mime_type, image_type),
        "message": f"{image_type.title()} image generated with {provider_status()['name']}.",
        "provider": provider_status(),
    }
