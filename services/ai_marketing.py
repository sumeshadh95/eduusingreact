
"""ai_marketing.py - AI marketing copy, images, brochures, and recruitment email."""

import logging
import time

from services.ai_core import (
    _brief_error,
    _clear_error,
    _generate_image_with_gemini,
    _generate_image_with_imagen,
    _generate_text,
    _gemini_image_model_candidates,
    _get_provider_config,
    _imagen_model_candidates,
    _is_image_access_error,
    _parse_json_response,
    _remember_error,
)

logger = logging.getLogger(__name__)

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
