"""Validate JSON responses from AI text generation."""

from services.ai_errors import brief_error, clear_error, remember_error
from services.ai_text_client import parse_json_response


def parse_validated_json(
    raw: str,
    *,
    validator,
    success_message: str,
    missing_message: str,
    parse_prefix: str,
    warning_template: str,
    logger,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> tuple:
    try:
        data = parse_json_response(raw)
    except exceptions as exc:
        logger.warning(warning_template, exc)
        remember_error(brief_error("AI", parse_prefix, exc))
        return (None, True)

    if validator(data):
        logger.info(success_message)
        clear_error()
        return (data, False)

    remember_error(missing_message)
    return (None, True)
