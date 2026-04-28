"""Gemini image-generation client."""

from services.ai_http import response_json
from services.ai_image_extractors import extract_inline_image


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
