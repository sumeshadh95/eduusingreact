"""Retry helpers shared by AI clients."""

import time

RETRYABLE_MARKERS = ["503", "high demand", "unavailable", "connection", "timeout", "temporarily"]


def retryable_provider_error(error: Exception) -> bool:
    detail = str(error).lower()
    return any(marker in detail for marker in RETRYABLE_MARKERS)


def retry_call(operation, attempts: int) -> tuple[object, Exception]:
    last_error = None
    for attempt in range(attempts):
        try:
            return (operation(), None)
        except Exception as exc:
            last_error = exc
            if should_retry(exc, attempt, attempts):
                time.sleep(1 + attempt)
                continue
            return (None, last_error)
    return (None, last_error)


def should_retry(error: Exception, attempt: int, attempts: int) -> bool:
    return retryable_provider_error(error) and attempt < attempts - 1
