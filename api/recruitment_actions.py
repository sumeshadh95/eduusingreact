"""Recruitment email route actions."""

from api.config import effective_api_key, provider_status
from api.serializers import snake_programme
from services import ai_service


def generate_recruitment_email_payload(candidate: dict, programme_payload: dict, course: dict) -> dict:
    email, used_fallback = ai_service.generate_recruitment_email(
        candidate,
        snake_programme(programme_payload),
        course,
        api_key=effective_api_key(),
    )
    return {
        "email": email,
        "usedFallback": used_fallback,
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }
