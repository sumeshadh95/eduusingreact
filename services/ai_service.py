"""ai_service.py - Compatibility facade for AI generation modules."""

from services.ai_core import get_active_provider_name, get_last_error
from services.ai_curriculum import (
    analyze_course_difficulty,
    generate_programme_content,
    summarize,
)
from services.ai_marketing import (
    generate_brochure,
    generate_marketing_content,
    generate_marketing_image,
    generate_recruitment_email,
)
from services.ai_personalization import (
    generate_chapter_text_patch,
    generate_minigame_question,
    generate_personalized_chapters,
)

__all__ = [
    "analyze_course_difficulty",
    "generate_brochure",
    "generate_chapter_text_patch",
    "generate_marketing_content",
    "generate_marketing_image",
    "generate_minigame_question",
    "generate_personalized_chapters",
    "generate_programme_content",
    "generate_recruitment_email",
    "get_active_provider_name",
    "get_last_error",
    "summarize",
]
