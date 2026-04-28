"""Gemini inline image response parsing."""

import base64


def extract_inline_image(data: dict) -> tuple:
    inline = next((item for item in inline_images(data) if item.get("data")), None)
    if not inline:
        raise RuntimeError("Gemini returned no image data.")
    return decoded_image(inline["data"], inline.get("mimeType") or inline.get("mime_type"))


def inline_images(data: dict) -> list[dict]:
    return [
        part.get("inlineData") or part.get("inline_data") or {}
        for candidate in data.get("candidates") or []
        for part in candidate.get("content", {}).get("parts", [])
    ]


def decoded_image(encoded: str, mime_type: str = None) -> tuple:
    return (base64.b64decode(encoded), mime_type or "image/png")
