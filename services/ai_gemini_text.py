"""Gemini text-generation client."""

from services.ai_gemini_payload import extract_gemini_text, gemini_payload
from services.ai_gemini_retry import generate_with_gemini_fallbacks
from services.ai_http import response_json


def generate_with_gemini(
    system_prompt: str,
    user_prompt: str,
    *,
    api_key: str,
    model: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool = False,
) -> str:
    import requests

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        json=gemini_payload(system_prompt, user_prompt, max_tokens, temperature, json_mode),
        timeout=60,
    )
    data = response_json(response)
    if response.status_code >= 400:
        detail = data.get("error", {}).get("message") or response.text
        raise RuntimeError(f"Gemini returned HTTP {response.status_code}: {detail}")
    return extract_gemini_text(data)


def generate_with_gemini_model_fallbacks(
    key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool,
) -> str:
    return generate_with_gemini_fallbacks(
        lambda candidate: generate_with_gemini(
            system_prompt,
            user_prompt,
            api_key=key,
            model=candidate,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=json_mode,
        ),
        model,
    )
