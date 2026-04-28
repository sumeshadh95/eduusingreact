"""Imagen image-generation client."""

from services.ai_http import response_json
from services.ai_image_extractors import extract_imagen_prediction


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
