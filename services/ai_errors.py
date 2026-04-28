"""Shared AI fallback messages and UI-facing error state."""

from services.ai_error_matcher import error_message

FALLBACK_SUMMARY = (
    "This course introduces the fundamentals of game development, covering "
    "game design principles, storytelling and narrative design, player experience, "
    "basic programming logic, game mechanics, prototyping, and testing. Students "
    "will learn how to design engaging interactive experiences, build simple game "
    "prototypes using industry-standard tools, and iterate based on playtesting "
    "feedback. The course culminates in a final prototype presentation where "
    "students demonstrate their game concept, design decisions, and development "
    "process. Suitable for beginners with an interest in creative technology "
    "and interactive media."
)

_LAST_ERROR = None


def remember_error(message: str) -> None:
    global _LAST_ERROR
    _LAST_ERROR = (message or "").strip()


def clear_error() -> None:
    global _LAST_ERROR
    _LAST_ERROR = None


def get_last_error() -> str:
    return _LAST_ERROR or ""


def brief_error(provider: str, prefix: str, error: Exception) -> str:
    return error_message(str(error), provider, prefix, ERROR_HANDLERS, short_detail)


def short_detail(detail: str) -> str:
    return detail[:217].rstrip() + "..." if len(detail) > 220 else detail


def paid_plan_message(provider: str) -> str:
    return (
        f"{provider} image generation requires a paid/quota-enabled Gemini API "
        "project for this model. Enable billing or use a key with image quota, "
        "then click Generate again."
    )


def quota_message(provider: str) -> str:
    return (
        f"{provider} returned a quota or billing error. Check the API key's "
        "billing/quota, then click Regenerate with AI again."
    )


def invalid_key_message(provider: str) -> str:
    return f"{provider} rejected the API key. Check the key in the .env file."


ERROR_HANDLERS = [
    (["paid plan", "upgrade your account"], paid_plan_message),
    (["insufficient_quota", "quota", "billing"], quota_message),
    (["api key not valid", "invalid api key", "permission"], invalid_key_message),
]
