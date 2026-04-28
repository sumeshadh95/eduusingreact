"""Result objects for image model attempts."""

from services.ai_image_errors import is_image_access_error


def success_result(image_result: tuple) -> dict:
    image_bytes, mime_type = image_result
    return {"image": image_bytes, "mime": mime_type, "error": None, "access_error": None}


def failure_result(error: Exception) -> dict:
    return {"image": None, "mime": None, "error": error, "access_error": access_error(error)}


def empty_result() -> dict:
    return {"image": None, "mime": None, "error": None, "access_error": None}


def merge_results(current: dict, latest: dict) -> dict:
    return {
        "image": latest["image"] or current["image"],
        "mime": latest["mime"] or current["mime"],
        "error": latest["error"] or current["error"],
        "access_error": latest["access_error"] or current["access_error"],
    }


def access_error(error: Exception) -> Exception | None:
    return error if error and is_image_access_error(error) else None
