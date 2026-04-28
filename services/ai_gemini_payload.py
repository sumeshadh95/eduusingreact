"""Gemini text payload and response extraction."""


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
    text = "".join(part.get("text", "") for part in first_candidate_parts(candidates)).strip()
    if text:
        return text
    finish_reason = candidates[0].get("finishReason", "unknown")
    raise RuntimeError(f"Gemini returned no text. Finish reason: {finish_reason}.")


def first_candidate_parts(candidates: list[dict]) -> list[dict]:
    return candidates[0].get("content", {}).get("parts", [])
