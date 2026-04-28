"""Gemini text-generation client."""

import logging
import time

from services.ai_http import response_json
from services.ai_provider_config import gemini_model_candidates

logger = logging.getLogger(__name__)


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


def generate_with_gemini_fallbacks(
    key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool,
) -> str:
    last_error = None
    for candidate_model in gemini_model_candidates(model):
        text, last_error = try_gemini_model(
            candidate_model, key, system_prompt, user_prompt, max_tokens, temperature, json_mode
        )
        if text:
            log_success(candidate_model, model)
            return text
    raise last_error or RuntimeError("Gemini generation failed.")


def try_gemini_model(
    model: str,
    key: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool,
) -> tuple[str, Exception]:
    last_error = None
    for attempt in range(3):
        try:
            return (
                generate_with_gemini(
                    system_prompt,
                    user_prompt,
                    api_key=key,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode,
                ),
                None,
            )
        except Exception as exc:
            last_error = exc
            if retryable_text_error(exc) and attempt < 2:
                time.sleep(1 + attempt)
                continue
            break
    return (None, last_error)


def gemini_payload(
    system_prompt: str, user_prompt: str, max_tokens: int, temperature: float, json_mode: bool
) -> dict:
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"
    return payload


def extract_gemini_text(data: dict) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if text:
        return text
    finish_reason = candidates[0].get("finishReason", "unknown")
    raise RuntimeError(f"Gemini returned no text. Finish reason: {finish_reason}.")


def retryable_text_error(error: Exception) -> bool:
    detail = str(error).lower()
    return any(
        marker in detail
        for marker in ["503", "high demand", "unavailable", "connection", "timeout", "temporarily"]
    )


def log_success(candidate_model: str, configured_model: str) -> None:
    if candidate_model != configured_model:
        logger.info("Gemini generation used fallback model %s.", candidate_model)
    logger.info("Gemini generation completed successfully.")
