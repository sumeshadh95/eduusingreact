"""Gemini inline image response parsing."""

import base64

from services.ai_inline_image_finder import first_inline_image


def extract_inline_image(data: dict) -> tuple:
    inline = first_inline_image(data)
    if not inline:
        raise RuntimeError("Gemini returned no image data.")
    return decoded_image(inline["data"], inline.get("mimeType") or inline.get("mime_type"))


def decoded_image(encoded: str, mime_type: str = None) -> tuple:
    return (base64.b64decode(encoded), mime_type or "image/png")
