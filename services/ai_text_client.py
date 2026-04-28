"""Text generation dispatch."""

from services.ai_errors import clear_error
from services.ai_generation_failure import remember_generation_failure
from services.ai_gemini_text import generate_with_gemini_model_fallbacks
from services.ai_json_response import parse_json_response
from services.ai_openai_text import generate_with_openai
from services.ai_provider_config import get_provider_config


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
        return generate_with_gemini_model_fallbacks(
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
