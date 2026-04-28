"""Runtime configuration for the CoursePilot API."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from services import ai_service

BASE_DIR = Path(__file__).resolve().parents[1]
ASSET_DIR = BASE_DIR / "generated_assets"


def load_environment() -> None:
    load_dotenv(BASE_DIR / ".env", override=True)


def effective_api_key() -> str:
    load_environment()
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
        or os.environ.get("OPENAI_API_KEY", "").strip()
    )


def provider_status() -> dict[str, Any]:
    load_environment()
    provider_name = ai_service.get_active_provider_name(effective_api_key())
    model_var = "GEMINI_MODEL" if provider_name == "Gemini" else "OPENAI_MODEL"
    return {
        "name": provider_name,
        "hasKey": bool(effective_api_key()),
        "model": os.environ.get(model_var, "").strip(),
        "lastError": ai_service.get_last_error(),
    }
