"""Prompt templates for marketing-image generation."""


def marketing_image_prompt(programme_title: str, content: dict, image_type: str) -> tuple[str, str]:
    template = social_prompt if image_type == "social" else brochure_prompt
    aspect_ratio = "1:1" if image_type == "social" else "3:4"
    return (template(programme_title, content), aspect_ratio)


def social_prompt(programme_title: str, content: dict) -> str:
    return f"""Create a beautiful, polished square social media image for Xamk's short programme "{programme_title}".
Visual direction: modern university marketing, energetic game development theme, students designing prototypes with laptops and game controllers, subtle Finland/Xamk academic feel, clean composition, Xamk green and deep blue brand accents, readable space for caption overlay, no tiny unreadable text.
Tagline inspiration: {content.get("tagline", "")}
Style: professional, bright, credible, premium, demo-ready."""


def brochure_prompt(programme_title: str, content: dict) -> str:
    return f"""Create a beautiful professional brochure/pamphlet cover image for Xamk's short programme "{programme_title}".
Visual direction: A4-style cover, game development sprint theme, creative technology classroom, prototype screens, approachable university continuing education, Xamk green and deep blue brand accents, clean layout space for title and dates, no tiny unreadable text.
Website copy inspiration: {content.get("website", "")}
Style: premium university brochure, polished, credible, demo-ready."""
