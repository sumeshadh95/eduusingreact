"""Match provider error details to UI-facing messages."""


def error_message(detail: str, provider: str, prefix: str, handlers: list, shortener) -> str:
    handler = matching_handler(detail, handlers)
    return handler(provider) if handler else f"{prefix}: {shortener(detail)}"


def matching_handler(detail: str, handlers: list):
    lowered = detail.lower()
    return next((handler for markers, handler in handlers if contains_marker(lowered, markers)), None)


def contains_marker(detail: str, markers: list[str]) -> bool:
    return any(marker in detail for marker in markers)
