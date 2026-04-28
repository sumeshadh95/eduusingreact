"""
ai_service.py - AI generation for summaries, personalization, marketing, and brochures.

Gemini is used first when GEMINI_API_KEY or GOOGLE_API_KEY is available.
OpenAI is still supported through OPENAI_API_KEY. Functions NEVER raise;
all errors are caught and fallback content is returned.
No streamlit imports.
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


def summarize(text: str, api_key: str = None) -> tuple:
    """
    Summarize course material text using the configured AI provider.

    Returns:
        tuple of (summary: str, used_fallback: bool)
    """
    summary = _generate_text(
        (
            "You are a helpful academic assistant. Summarize the following "
            "course material in one concise paragraph (3-5 sentences). Focus "
            "on what the student will learn and the key topics covered."
        ),
        text,
        max_tokens=300,
        temperature=0.5,
        api_key=api_key,
    )
    if summary:
        return (summary, False)
    logger.info("AI summary unavailable - using fallback summary.")
    return (FALLBACK_SUMMARY, True)


def analyze_course_difficulty(
    course: dict,
    material_text: str,
    summary: str,
    api_key: str = None,
) -> tuple:
    """
    Analyze course difficulty with the configured AI provider.

    Returns:
        tuple of (data: dict with level/rationale/signals, used_fallback: bool)
    """
    course_name = course.get("course_name", "")
    course_description = course.get("description", "")
    keywords = ", ".join(course.get("keywords", []))
    material_preview = (material_text or "")[:3500]

    prompt = f"""Analyze the difficulty of this short programme source course.

Course name: {course_name}
Description: {course_description}
Keywords: {keywords}
Material summary: {summary}
Material excerpt: {material_preview}

Classify the learner difficulty as exactly one of: Easy, Medium, Hard.

Use this rubric:
- Easy: beginner friendly, low prerequisite knowledge, mostly conceptual or guided practice
- Medium: some technical concepts, practice tasks, or tool use but still accessible with guidance
- Hard: advanced prerequisites, dense technical depth, independent complex projects, or specialist knowledge

Return ONLY valid JSON with this structure:
{{
  "level": "Easy | Medium | Hard",
  "rationale": "One concise sentence explaining why",
  "signals": ["Signal 1", "Signal 2", "Signal 3"]
}}"""

    raw = _generate_text(
        "You are a university curriculum analyst. Always respond with valid JSON only.",
        prompt,
        max_tokens=700,
        temperature=0.25,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (
            {
                "level": "Medium",
                "rationale": "The course combines beginner concepts with practical tool-based project work.",
                "signals": ["Beginner-facing source course", "Hands-on project work", "Guided short programme format"],
            },
            True,
        )

    try:
        data = _parse_json_response(raw)
        level = str(data.get("level", "Medium")).strip().title()
        if level not in {"Easy", "Medium", "Hard"}:
            level = "Medium"
        data["level"] = level
        data["rationale"] = data.get("rationale") or "The course has a balanced mix of theory and applied tasks."
        data["signals"] = data.get("signals") or []
        _clear_error()
        return (data, False)
    except Exception as e:
        logger.warning("AI difficulty parse error (%s) - using fallback.", e)
        _remember_error(_brief_error("AI", "Could not parse AI difficulty response", e))
        return (
            {
                "level": "Medium",
                "rationale": "The course combines beginner concepts with practical tool-based project work.",
                "signals": ["Beginner-facing source course", "Hands-on project work", "Guided short programme format"],
            },
            True,
        )


def generate_programme_content(
    course: dict,
    teacher: dict,
    trend: dict,
    weeks: int,
    ects: int,
    summary: str,
    api_key: str = None,
    approach: str = None,
) -> tuple:
    """
    Generate a short programme plan using the configured AI provider.

    Returns:
        tuple of (programme: dict, used_fallback: bool)
    """
    teacher_name = teacher.get("name", "")
    available_months = teacher.get("available_months", [])
    course_name = course.get("course_name", "")
    trend_name = trend.get("trend", "")
    keywords = ", ".join(trend.get("keywords", []))
    approach_instruction = (
        f"\nAlternative approach requested: {approach}. Make the whole programme structure, framing, title, outcomes, weekly activities, and assessment reflect this approach while staying credible for Xamk."
        if approach
        else ""
    )

    prompt = f"""Create a demo-ready university short programme plan.

Matched course: {course_name}
Trend: {trend_name}
Trend keywords: {keywords}
Recommended duration: {weeks} weeks
Credits: {ects} ECTS
Teacher: {teacher_name}
Available months: {", ".join(available_months)}
Course material summary: {summary}
{approach_instruction}

Return ONLY valid JSON with this exact structure:
{{
  "title": "A concise, marketable programme title",
  "based_on": "{course_name}",
  "ects": {ects},
  "duration_weeks": {weeks},
  "mode": "Online / Hybrid",
  "teacher": "{teacher_name}",
  "teacher_id": "{teacher.get("teacher_id", "")}",
  "available_months": ["month names copied from the teacher availability"],
  "target_students": "Specific target learner group in 1-2 sentences",
  "learning_outcomes": [
    "Outcome 1",
    "Outcome 2",
    "Outcome 3"
  ],
  "weekly_structure": {{
    "Week 1": [
      "Topic title - concrete activity students do",
      "Topic title - concrete activity students do",
      "Topic title - concrete activity students do"
    ]
  }},
  "assessment": "Short description of how students complete the 3 ECTS work",
  "demo_pitch": "One persuasive sentence explaining why this programme should run now"
}}

Make the programme feel current, practical, and credible for Xamk continuing education. Create exactly {weeks} week entries."""

    raw = _generate_text(
        "You are a senior curriculum designer for Xamk short programmes. Always respond with valid JSON only.",
        prompt,
        max_tokens=1800,
        temperature=0.65,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        required = ["title", "weekly_structure", "target_students"]
        if all(data.get(key) for key in required):
            data["based_on"] = data.get("based_on") or course_name
            data["ects"] = data.get("ects") or ects
            data["duration_weeks"] = data.get("duration_weeks") or weeks
            data["teacher"] = data.get("teacher") or teacher_name
            data["teacher_id"] = data.get("teacher_id") or teacher.get("teacher_id", "")
            data["available_months"] = data.get("available_months") or available_months
            data["mode"] = data.get("mode") or "Online / Hybrid"
            logger.info("AI programme generated successfully.")
            _clear_error()
            return (data, False)
        _remember_error("AI programme response was missing required fields.")
        return (None, True)
    except Exception as e:
        logger.warning("AI programme parse error (%s) - using fallback.", e)
        _remember_error(_brief_error("AI", "Could not parse AI programme response", e))
        return (None, True)


def generate_personalized_chapters(
    course_name: str, student_field: str, api_key: str = None
) -> tuple:
    """
    Generate personalized learning chapters using the configured AI provider.

    Returns:
        tuple of (data: dict with 'chapters' and 'final_assignment', used_fallback: bool)
    """
    prompt = f"""Create 5 learning chapters for a course called "{course_name}" personalized for a {student_field} student.

For each chapter, provide:
1. A chapter title relevant to the course content
2. A standard explanation (2-3 sentences) of what this chapter covers
3. A personalized explanation (2-3 sentences) showing how this chapter's topic connects to the {student_field} field specifically
4. A simple playable mini-game concept that helps {student_field} students learn through gamification. Each game must include a scenario, four choices, the correct choice text, and feedback.

Also provide a final assignment description (3-4 sentences) that bridges {course_name} with {student_field}.

Return ONLY valid JSON with this exact structure, no markdown formatting:
{{
  "chapters": [
    {{
      "title": "Chapter 1 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }},
    {{
      "title": "Chapter 2 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }},
    {{
      "title": "Chapter 3 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }},
    {{
      "title": "Chapter 4 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }},
    {{
      "title": "Chapter 5 - [Title]",
      "standard_explanation": "...",
      "personalized_explanation": "...",
      "minigame": {{
        "name": "[Creative Game Name]",
        "description": "...",
        "scenario": "A short decision challenge for the learner",
        "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
        "correct_choice": "Exact text of the correct choice",
        "feedback": "Brief explanation of why the answer works"
      }}
    }}
  ],
  "final_assignment": "..."
}}

Make the content educational, creative, and specifically relevant to how {student_field} students can benefit from learning {course_name}."""

    raw = _generate_text(
        "You are an expert educational content designer. Always respond with valid JSON only.",
        prompt,
        max_tokens=2000,
        temperature=0.7,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        if "chapters" in data and len(data["chapters"]) >= 5:
            logger.info("AI personalized chapters generated successfully.")
            _clear_error()
            return (data, False)
        _remember_error("AI personalization response was missing chapters.")
        return (None, True)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.warning("Failed to parse AI personalization response (%s) - using fallback.", e)
        _remember_error(_brief_error("AI", "Could not parse AI personalization response", e))
        return (None, True)


def generate_minigame_question(
    course_name: str,
    student_field: str,
    chapter: dict,
    api_key: str = None,
) -> tuple:
    """
    Generate one editable mini-game question for a chapter.

    Returns:
        tuple of (minigame: dict, used_fallback: bool)
    """
    prompt = f"""Generate one simple playable mini-game question for this learning chapter.

Course: {course_name}
Student field: {student_field}
Chapter title: {chapter.get("title", "")}
Standard explanation: {chapter.get("standard_explanation", "")}
Personalized explanation: {chapter.get("personalized_explanation", "")}

The question is for an admin-authored personalized learning experience. Make it concrete, useful, and connected to {student_field}. It should be suitable for a student to answer inside a course app.

Return ONLY valid JSON with this exact structure:
{{
  "name": "Short game name",
  "description": "One-sentence description of the mini-game",
  "scenario": "A short decision challenge written as the question the student sees",
  "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
  "correct_choice": "Exact text of the correct choice",
  "feedback": "Brief explanation of why the correct answer is best"
}}"""

    raw = _generate_text(
        "You are an educational game designer. Always respond with valid JSON only.",
        prompt,
        max_tokens=900,
        temperature=0.75,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        choices = data.get("choices", [])
        correct = data.get("correct_choice", "")
        if data.get("scenario") and len(choices) >= 2:
            if correct not in choices:
                data["correct_choice"] = choices[0]
            _clear_error()
            return (data, False)
        _remember_error("AI question response was missing scenario or choices.")
        return (None, True)
    except Exception as e:
        logger.warning("AI question parse error (%s) - using existing question.", e)
        _remember_error(_brief_error("AI", "Could not parse AI question response", e))
        return (None, True)


def generate_chapter_text_patch(
    course_name: str,
    student_field: str,
    chapter: dict,
    api_key: str = None,
) -> tuple:
    """
    Generate missing chapter title/explanation copy without changing the game.

    Returns:
        tuple of (chapter_text: dict, used_fallback: bool)
    """
    game = chapter.get("minigame", {}) or {}
    prompt = f"""Write polished chapter text for an admin-edited personalized learning module.

Course: {course_name}
Student field: {student_field}
Current chapter title: {chapter.get("title", "")}
Current standard explanation: {chapter.get("standard_explanation", "")}
Current personalized explanation: {chapter.get("personalized_explanation", "")}
Mini-game name: {game.get("name", "")}
Mini-game description: {game.get("description", "")}
Mini-game scenario: {game.get("scenario", "")}

Return ONLY valid JSON with this exact structure:
{{
  "title": "Short chapter title",
  "standard_explanation": "A clear 2-3 sentence explanation for any student.",
  "personalized_explanation": "A clear 2-3 sentence explanation that connects the same topic to {student_field} practice."
}}"""

    raw = _generate_text(
        "You are an expert instructional designer. Always respond with valid JSON only.",
        prompt,
        max_tokens=850,
        temperature=0.65,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        required = ["title", "standard_explanation", "personalized_explanation"]
        if all(str(data.get(key, "")).strip() for key in required):
            _clear_error()
            return (data, False)
        _remember_error("AI chapter text response was missing title or explanations.")
        return (None, True)
    except Exception as e:
        logger.warning("AI chapter text parse error (%s).", e)
        _remember_error(_brief_error("AI", "Could not parse AI chapter text response", e))
        return (None, True)


def generate_marketing_content(
    programme_title: str, course_name: str, weeks: int, ects: int, api_key: str = None
) -> tuple:
    """
    Generate marketing content using the configured AI provider.

    Returns:
        tuple of (data: dict with website/social/email/tagline/selling_points, used_fallback: bool)
    """
    prompt = f"""Generate marketing content for a university short programme called "{programme_title}" based on the course "{course_name}". It is a {weeks}-week, {ects} ECTS online programme by Xamk university.

Return ONLY valid JSON with this exact structure, no markdown:
{{
  "website": "A compelling website description (3-4 sentences) for the programme page.",
  "social": "A social media post with emojis and hashtags promoting the programme.",
  "email": "A professional partner school email (Dear Partner format) announcing the programme.",
  "tagline": "A catchy one-line tagline for the programme.",
  "selling_points": [
    "First selling point (1-2 sentences about industry relevance).",
    "Second selling point (1-2 sentences about accessibility).",
    "Third selling point (1-2 sentences about flexibility and credits)."
  ]
}}"""

    raw = _generate_text(
        "You are an expert university marketing copywriter. Always respond with valid JSON only.",
        prompt,
        max_tokens=1500,
        temperature=0.7,
        api_key=api_key,
        json_mode=True,
    )
    if not raw:
        return (None, True)

    try:
        data = _parse_json_response(raw)
        if "website" in data and "selling_points" in data:
            logger.info("AI marketing content generated successfully.")
            _clear_error()
            return (data, False)
        _remember_error("AI marketing response was missing required fields.")
        return (None, True)
    except Exception as e:
        logger.warning("AI marketing parse error (%s) - using fallback.", e)
        _remember_error(_brief_error("AI", "Could not parse AI marketing response", e))
    return (None, True)


def generate_marketing_image(
    programme_title: str,
    content: dict,
    image_type: str,
    api_key: str = None,
) -> tuple:
    """
    Generate one marketing image with Gemini.

    Returns:
        tuple of (image_bytes: bytes, mime_type: str, used_fallback: bool)
    """
    provider, key, _ = _get_provider_config(api_key)
    if provider != "gemini" or not key:
        _remember_error("Gemini image generation requires GEMINI_API_KEY in .env.")
        return (None, None, True)

    if image_type == "social":
        aspect_ratio = "1:1"
        prompt = f"""Create a beautiful, polished square social media image for Xamk's short programme "{programme_title}".
Visual direction: modern university marketing, energetic game development theme, students designing prototypes with laptops and game controllers, subtle Finland/Xamk academic feel, clean composition, Xamk green and deep blue brand accents, readable space for caption overlay, no tiny unreadable text.
Tagline inspiration: {content.get("tagline", "")}
Style: professional, bright, credible, premium, demo-ready."""
    else:
        aspect_ratio = "3:4"
        prompt = f"""Create a beautiful professional brochure/pamphlet cover image for Xamk's short programme "{programme_title}".
Visual direction: A4-style cover, game development sprint theme, creative technology classroom, prototype screens, approachable university continuing education, Xamk green and deep blue brand accents, clean layout space for title and dates, no tiny unreadable text.
Website copy inspiration: {content.get("website", "")}
Style: premium university brochure, polished, credible, demo-ready."""

    last_error = None
    access_error = None
    for model in _imagen_model_candidates():
        for attempt in range(2):
            try:
                image_bytes, mime_type = _generate_image_with_imagen(
                    prompt,
                    api_key=key,
                    model=model,
                    aspect_ratio=aspect_ratio,
                )
                logger.info("Imagen image generated with %s.", model)
                _clear_error()
                return (image_bytes, mime_type, False)
            except Exception as e:
                last_error = e
                if _is_image_access_error(e) and access_error is None:
                    access_error = e
                detail = str(e).lower()
                retryable = any(
                    marker in detail
                    for marker in ["503", "high demand", "unavailable", "connection", "timeout", "temporarily"]
                )
                if retryable and attempt < 1:
                    time.sleep(1)
                    continue
                break

    for model in _gemini_image_model_candidates():
        for attempt in range(3):
            try:
                image_bytes, mime_type = _generate_image_with_gemini(
                    prompt,
                    api_key=key,
                    model=model,
                )
                logger.info("Gemini image generated with %s.", model)
                _clear_error()
                return (image_bytes, mime_type, False)
            except Exception as e:
                last_error = e
                if _is_image_access_error(e) and access_error is None:
                    access_error = e
                detail = str(e).lower()
                retryable = any(
                    marker in detail
                    for marker in ["503", "high demand", "unavailable", "connection", "timeout", "temporarily"]
                )
                if retryable and attempt < 2:
                    time.sleep(1 + attempt)
                    continue
                break

    final_error = access_error or last_error
    _remember_error(_brief_error("Gemini", "Gemini image generation failed", final_error))
    logger.warning("Gemini image generation failed (%s).", final_error)
    return (None, None, True)


def generate_recruitment_email(
    candidate: dict,
    programme: dict,
    course: dict,
    api_key: str = None,
) -> tuple:
    """
    Generate a first-touch recruitment email for a probable teacher candidate.

    Returns:
        tuple of (email_text: str, used_fallback: bool)
    """
    prompt = f"""Write a warm, professional recruitment outreach email from Xamk Continuing Education to this candidate.

Candidate name: {candidate.get("name", "")}
Candidate headline: {candidate.get("headline", "")}
Candidate skills: {", ".join(candidate.get("skills", []))}
Candidate notes: {candidate.get("notes", "")}
Programme: {programme.get("title", "")}
Based on course: {course.get("course_name", "")}
Delivery mode: {programme.get("mode", "Online / Hybrid")}
Duration and credits: {programme.get("duration_weeks", "")} weeks, {programme.get("ects", "")} ECTS

Goal:
- Say Xamk is interested in going further with recruiting them and knowing them more.
- Ask for more details about their teaching availability and relevant experience.
- Explicitly ask them to send their latest CV and any additional recruitment documents, certificates, portfolio links, or teaching references that Xamk may use in the recruitment process.
- Mention that their background looks relevant to the programme.
- Keep the tone respectful, concise, and not pushy.
- Include a clear subject line.
- Do not omit the CV/documents request.

Return only the email text."""

    email = _generate_text(
        "You are a careful university HR recruiter writing concise candidate outreach emails.",
        prompt,
        max_tokens=700,
        temperature=0.45,
        api_key=api_key,
    )
    if email:
        return (email, False)

    fallback = f"""Subject: Exploring teaching collaboration with Xamk

Dear {candidate.get("name", "Candidate")},

I hope you are doing well. We are exploring teachers for Xamk's {programme.get("title", "new short programme")}, and your background in {", ".join(candidate.get("skills", [])[:3])} looks highly relevant.

We would like to go further with recruiting you and learn more about your experience, teaching availability, and interest in contributing to this programme. Could you please share your latest CV and any additional documents or portfolio materials that Xamk may use as part of the recruitment process?

It would also be helpful to know your preferred teaching modes, available months, and examples of previous teaching, training, or project work related to this topic.

Best regards,
Xamk Continuing Education"""
    return (fallback, True)


def generate_brochure(
    programme_title: str,
    course_name: str,
    weeks: int,
    ects: int,
    weekly_structure: dict,
    api_key: str = None,
) -> tuple:
    """
    Generate a brochure/pamphlet text using the configured AI provider.

    Returns:
        tuple of (brochure_text: str, used_fallback: bool)
    """
    week_details = ""
    for week, topics in weekly_structure.items():
        week_details += f"\n{week}:\n" + "\n".join(f"  - {t}" for t in topics)

    prompt = f"""Create a professional marketing brochure text for a university short programme. Format it as a ready-to-print pamphlet with clear sections.

Programme: {programme_title}
Based on: {course_name}
Duration: {weeks} weeks | Credits: {ects} ECTS
Mode: Online / Hybrid
University: Xamk (South-Eastern Finland University of Applied Sciences)
Schedule: {week_details}

Create the brochure with these sections:
1. HEADLINE - a bold attention-grabbing title
2. PROGRAMME OVERVIEW - 2-3 sentences about what students will learn
3. WHO IS THIS FOR? - target audience description
4. PROGRAMME SCHEDULE - week-by-week highlights
5. KEY BENEFITS - 4-5 bullet points
6. PRACTICAL INFO - duration, credits, mode, dates
7. HOW TO ENROLL - call to action with next steps
8. TESTIMONIAL - a fictional but realistic student quote

Use clear formatting with headers, bullets, and line breaks. Make it compelling and professional."""

    brochure = _generate_text(
        "You are an expert university marketing designer creating professional programme brochures.",
        prompt,
        max_tokens=2000,
        temperature=0.7,
        api_key=api_key,
    )
    if brochure:
        logger.info("AI brochure generated successfully.")
        _clear_error()
        return (brochure, False)
    return (None, True)
