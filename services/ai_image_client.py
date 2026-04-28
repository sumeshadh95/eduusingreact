"""Gemini and Imagen image-generation clients."""

import base64

from services.ai_http import response_json


def generate_image_with_gemini(prompt: str, *, api_key: str, model: str) -> tuple:
    import requests

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        },
        timeout=90,
    )
    data = response_json(response)
    if response.status_code >= 400:
        detail = data.get("error", {}).get("message") or response.text
        raise RuntimeError(f"Gemini image model returned HTTP {response.status_code}: {detail}")
    return extract_inline_image(data)


def extract_inline_image(data: dict) -> tuple:
    for candidate in data.get("candidates") or []:
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                mime_type = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                return (base64.b64decode(inline["data"]), mime_type)
    raise RuntimeError("Gemini returned no image data.")


def generate_image_with_imagen(
    prompt: str,
    *,
    api_key: str,
    model: str,
    aspect_ratio: str,
) -> tuple:
    import requests

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        json=imagen_payload(prompt, aspect_ratio),
        timeout=120,
    )
    data = response_json(response)
    if response.status_code >= 400:
        detail = data.get("error", {}).get("message") or response.text
        raise RuntimeError(f"Imagen model returned HTTP {response.status_code}: {detail}")
    return extract_imagen_prediction(data)


def imagen_payload(prompt: str, aspect_ratio: str) -> dict:
    return {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
            "personGeneration": "allow_adult",
        },
    }


def extract_imagen_prediction(data: dict) -> tuple:
    for prediction in data.get("predictions") or []:
        encoded = prediction.get("bytesBase64Encoded") or prediction.get("image", {}).get("bytesBase64Encoded")
        if encoded:
            mime_type = prediction.get("mimeType") or prediction.get("image", {}).get("mimeType") or "image/png"
            return (base64.b64decode(encoded), mime_type)
    raise RuntimeError("Imagen returned no image data.")


def is_image_access_error(error: Exception) -> bool:
    detail = str(error).lower()
    return any(
        marker in detail
        for marker in [
            "quota",
            "billing",
            "paid plan",
            "upgrade your account",
            "limit 0",
            "permission",
            "api key not valid",
        ]
    )
