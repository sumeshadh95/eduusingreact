"""Compatibility facade for AI marketing helpers."""

from services.ai_brochure import generate_brochure
from services.ai_marketing_copy import generate_marketing_content
from services.ai_marketing_images import generate_marketing_image
from services.ai_recruitment import generate_recruitment_email

__all__ = [
    "generate_brochure",
    "generate_marketing_content",
    "generate_marketing_image",
    "generate_recruitment_email",
]
