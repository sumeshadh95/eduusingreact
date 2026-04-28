"""Text generation dispatch and JSON parsing."""

import json
import logging

from services.ai_errors import brief_error, clear_error, remember_error
from services.ai_gemini_text import generate_with_gemini_fallbacks
from services.ai_openai_text import generate_with_openai
from services.ai_provider_config import get_provider_config

logger = logging.getLogger(__name__)


def generate_text(
    system_prompt: str,
    user_prompt: str,
    *,
    max_tokens: int,
    temperature: float,
    api_key: str = None,
    json_mode: bool = False,
) -> str:
    provider, key, model = get_provider_config(api_key)
    if not provider or not key:
        return None
    try:
        text = dispatch_text_generation(
            provider, key, model, system_prompt, user_prompt, max_tokens, temperature, json_mode
        )
        clear_error()
        return text
    except Exception as exc:
        remember_generation_failure(provider, exc)
        return None


def dispatch_text_generation(
    provider: str,
    key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool,
) -> str:
    if provider == "gemini":
        return generate_with_gemini_fallbacks(
            key, model, system_prompt, user_prompt, max_tokens, temperature, json_mode
        )
    return generate_with_openai(
        system_prompt,
        user_prompt,
        api_key=key,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


def remember_generation_failure(provider: str, error: Exception) -> None:
    provider_name = "Gemini" if provider == "gemini" else "OpenAI"
    logger.warning("%s generation failed (%s) - using fallback.", provider_name, error)
    remember_error(brief_error(provider_name, f"{provider_name} generation failed", error))


def parse_json_response(raw: str) -> dict:
    if not raw:
        return {}
    return json.loads(strip_markdown_json(raw.strip()))


def strip_markdown_json(raw: str) -> str:
    if not raw.startswith("```"):
        return raw
    raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    return raw[4:].strip() if raw.startswith("json") else raw
