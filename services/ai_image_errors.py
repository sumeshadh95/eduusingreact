"""Image-generation error classifiers."""

IMAGE_ACCESS_MARKERS = [
    "quota",
    "billing",
    "paid plan",
    "upgrade your account",
    "limit 0",
    "permission",
    "api key not valid",
]


def is_image_access_error(error: Exception) -> bool:
    detail = str(error).lower()
    return any(marker in detail for marker in IMAGE_ACCESS_MARKERS)
