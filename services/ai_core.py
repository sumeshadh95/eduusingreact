"""
ai_core.py - Shared AI provider/client helpers.

Gemini is used first when GEMINI_API_KEY or GOOGLE_API_KEY is available.
OpenAI is still supported through OPENAI_API_KEY. Functions NEVER raise;
all errors are caught and fallback content is returned.
"""

import base64
import json
import logging
import os
import time

logger = logging.getLogger(__name__)
_LAST_ERROR = None

FALLBACK_SUMMARY = (
    "This course introduces the fundamentals of game development, covering "
    "game design principles, storytelling and narrative design, player experience, "
    "basic programming logic, game mechanics, prototyping, and testing. Students "
    "will learn how to design engaging interactive experiences, build simple game "
    "prototypes using industry-standard tools, and iterate based on playtesting "
    "feedback. The course culminates in a final prototype presentation where "
    "students demonstrate their game concept, design decisions, and development "
    "process. Suitable for beginners with an interest in creative technology "
    "and interactive media."
)


def _remember_error(message: str):
    """Store the most recent AI failure for UI feedback."""
    global _LAST_ERROR
    _LAST_ERROR = (message or "").strip()


def _clear_error():
    global _LAST_ERROR
    _LAST_ERROR = None


def get_last_error() -> str:
    """Return the most recent AI failure message, if any."""
    return _LAST_ERROR or ""


def _brief_error(provider: str, prefix: str, error: Exception) -> str:
    """Convert provider exceptions into concise messages for the demo UI."""
    detail = str(error)
    lowered = detail.lower()
    if "paid plan" in lowered or "upgrade your account" in lowered:
        return (
            f"{provider} image generation requires a paid/quota-enabled Gemini API "
            "project for this model. Enable billing or use a key with image quota, "
            "then click Generate again."
        )
    if "insufficient_quota" in lowered or "quota" in lowered or "billing" in lowered:
        return (
            f"{provider} returned a quota or billing error. Check the API key's "
            "billing/quota, then click Regenerate with AI again."
        )
    if "api key not valid" in lowered or "invalid api key" in lowered or "permission" in lowered:
        return f"{provider} rejected the API key. Check the key in the .env file."
    if len(detail) > 220:
        detail = detail[:217].rstrip() + "..."
    return f"{prefix}: {detail}"


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def _default_gemini_model() -> str:
    return "gemini-2.0-flash"


def _gemini_model_candidates(model: str) -> list:
    """Prefer the configured model, then fall back to faster demo-safe models."""
    candidates = [
        model,
        _env("GEMINI_FALLBACK_MODEL"),
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-lite-latest",
    ]
    unique = []
    for candidate in candidates:
        candidate = (candidate or "").strip()
        if candidate.startswith("models/"):
            candidate = candidate.split("/", 1)[1]
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def _gemini_image_model_candidates() -> list:
    candidates = [
        _env("GEMINI_IMAGE_MODEL"),
        "gemini-3-pro-image-preview",
        "nano-banana-pro-preview",
        "gemini-3.1-flash-image-preview",
        "gemini-2.5-flash-image",
    ]
    unique = []
    for candidate in candidates:
        candidate = (candidate or "").strip()
        if candidate.startswith("models/"):
            candidate = candidate.split("/", 1)[1]
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def _imagen_model_candidates() -> list:
    candidates = [
        _env("GEMINI_IMAGEN_MODEL"),
        "imagen-4.0-generate-001",
        "imagen-4.0-fast-generate-001",
        "imagen-4.0-ultra-generate-001",
    ]
    unique = []
    for candidate in candidates:
        candidate = (candidate or "").strip()
        if candidate.startswith("models/"):
            candidate = candidate.split("/", 1)[1]
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def _get_provider_config(api_key: str = None) -> tuple:
    """Return (provider, api_key, model) for the configured AI provider."""
    requested = _env("AI_PROVIDER").lower()
    supplied_key = (api_key or "").strip()

    if supplied_key:
        use_gemini = (
            requested in {"gemini", "google"}
            or supplied_key.startswith("AIza")
            or supplied_key == _env("GEMINI_API_KEY")
            or supplied_key == _env("GOOGLE_API_KEY")
        )
        if use_gemini:
            return ("gemini", supplied_key, _env("GEMINI_MODEL") or _default_gemini_model())
        return ("openai", supplied_key, _env("OPENAI_MODEL") or "gpt-4o-mini")

    gemini_key = _env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY")
    openai_key = _env("OPENAI_API_KEY")

    if requested in {"gemini", "google"}:
        if not gemini_key:
            _remember_error("No GEMINI_API_KEY was found. Add it to .env and try again.")
            return (None, None, None)
        return ("gemini", gemini_key, _env("GEMINI_MODEL") or _default_gemini_model())

    if requested == "openai":
        if not openai_key:
            _remember_error("No OPENAI_API_KEY was found. Add it to .env and try again.")
            return (None, None, None)
        return ("openai", openai_key, _env("OPENAI_MODEL") or "gpt-4o-mini")

    if gemini_key:
        return ("gemini", gemini_key, _env("GEMINI_MODEL") or _default_gemini_model())
    if openai_key:
        return ("openai", openai_key, _env("OPENAI_MODEL") or "gpt-4o-mini")

    _remember_error("No AI API key was found. Add GEMINI_API_KEY or OPENAI_API_KEY to .env.")
    return (None, None, None)


def get_active_provider_name(api_key: str = None) -> str:
    """Return the currently configured provider display name."""
    provider, _, _ = _get_provider_config(api_key)
    if provider == "gemini":
        return "Gemini"
    if provider == "openai":
        return "OpenAI"
    return "AI"


def _generate_with_gemini(
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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        json=payload,
        timeout=60,
    )
    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.status_code >= 400:
        detail = data.get("error", {}).get("message") or response.text
        raise RuntimeError(f"Gemini returned HTTP {response.status_code}: {detail}")

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        finish_reason = candidates[0].get("finishReason", "unknown")
        raise RuntimeError(f"Gemini returned no text. Finish reason: {finish_reason}.")
    return text


def _generate_image_with_gemini(
    prompt: str,
    *,
    api_key: str,
    model: str,
) -> tuple:
    import requests

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    response = requests.post(
        url,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        json=payload,
        timeout=90,
    )
    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.status_code >= 400:
        detail = data.get("error", {}).get("message") or response.text
        raise RuntimeError(f"Gemini image model returned HTTP {response.status_code}: {detail}")

    candidates = data.get("candidates") or []
    for candidate in candidates:
        parts = candidate.get("content", {}).get("parts", [])
        for part in parts:
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                mime_type = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                return (base64.b64decode(inline["data"]), mime_type)

    raise RuntimeError("Gemini returned no image data.")


def _generate_image_with_imagen(
    prompt: str,
    *,
    api_key: str,
    model: str,
    aspect_ratio: str,
) -> tuple:
    import requests

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
            "personGeneration": "allow_adult",
        },
    }
    response = requests.post(
        url,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        json=payload,
        timeout=120,
    )
    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.status_code >= 400:
        detail = data.get("error", {}).get("message") or response.text
        raise RuntimeError(f"Imagen model returned HTTP {response.status_code}: {detail}")

    predictions = data.get("predictions") or []
    for prediction in predictions:
        encoded = (
            prediction.get("bytesBase64Encoded")
            or prediction.get("image", {}).get("bytesBase64Encoded")
        )
        if encoded:
            mime_type = prediction.get("mimeType") or prediction.get("image", {}).get("mimeType") or "image/png"
            return (base64.b64decode(encoded), mime_type)

    raise RuntimeError("Imagen returned no image data.")


def _is_image_access_error(error: Exception) -> bool:
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


def _generate_with_openai(
    system_prompt: str,
    user_prompt: str,
    *,
    api_key: str,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    import openai

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def _generate_text(
    system_prompt: str,
    user_prompt: str,
    *,
    max_tokens: int,
    temperature: float,
    api_key: str = None,
    json_mode: bool = False,
) -> str:
    provider, key, model = _get_provider_config(api_key)
    if not provider or not key:
        return None

    try:
        if provider == "gemini":
            text = None
            last_error = None
            for candidate_model in _gemini_model_candidates(model):
                for attempt in range(3):
                    try:
                        text = _generate_with_gemini(
                            system_prompt,
                            user_prompt,
                            api_key=key,
                            model=candidate_model,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            json_mode=json_mode,
                        )
                        break
                    except Exception as e:
                        last_error = e
                        detail = str(e).lower()
                        retryable = any(
                            marker in detail
                            for marker in [
                                "503",
                                "high demand",
                                "unavailable",
                                "connection",
                                "timeout",
                                "temporarily",
                            ]
                        )
                        if retryable and attempt < 2:
                            time.sleep(1 + attempt)
                            continue
                        break
                if text:
                    if candidate_model != model:
                        logger.info("Gemini generation used fallback model %s.", candidate_model)
                    break
            if not text and last_error:
                raise last_error
            logger.info("Gemini generation completed successfully.")
        else:
            text = _generate_with_openai(
                system_prompt,
                user_prompt,
                api_key=key,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            logger.info("OpenAI generation completed successfully.")
        _clear_error()
        return text
    except Exception as e:
        provider_name = "Gemini" if provider == "gemini" else "OpenAI"
        logger.warning("%s generation failed (%s) - using fallback.", provider_name, e)
        _remember_error(_brief_error(provider_name, f"{provider_name} generation failed", e))
        return None


def _parse_json_response(raw: str) -> dict:
    if not raw:
        return {}
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()
    return json.loads(raw)


