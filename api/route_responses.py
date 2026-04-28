"""Shared response helpers for route modules."""

from api.config import provider_status
from api.serializers import camel_marketing, camel_programme
from services import ai_service


def programme_response(programme: dict, used_fallback: bool) -> dict:
    return {
        "programme": camel_programme(programme),
        "programmeUsedFallback": used_fallback,
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }


def marketing_response(content: dict, used_fallback: bool) -> dict:
    return {
        "marketing": camel_marketing(content, used_fallback),
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }


def failed_question_response() -> dict:
    return {
        "ok": False,
        "message": ai_service.get_last_error() or "Question regeneration did not return a usable question.",
        "provider": provider_status(),
    }


def failed_image_response() -> dict:
    return {
        "ok": False,
        "message": ai_service.get_last_error() or "Gemini did not return image data.",
        "provider": provider_status(),
    }
