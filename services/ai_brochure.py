"""AI brochure text generation."""

import logging

from services.ai_core import _clear_error, _generate_text

logger = logging.getLogger(__name__)


def generate_brochure(
    programme_title: str,
    course_name: str,
    weeks: int,
    ects: int,
    weekly_structure: dict,
    api_key: str = None,
) -> tuple:
    brochure = _generate_text(
        "You are an expert university marketing designer creating professional programme brochures.",
        brochure_prompt(programme_title, course_name, weeks, ects, weekly_structure),
        max_tokens=2000,
        temperature=0.7,
        api_key=api_key,
    )
    if brochure:
        logger.info("AI brochure generated successfully.")
        _clear_error()
        return (brochure, False)
    return (None, True)


def brochure_prompt(
    programme_title: str,
    course_name: str,
    weeks: int,
    ects: int,
    weekly_structure: dict,
) -> str:
    return f"""Create a professional marketing brochure text for a university short programme. Format it as a ready-to-print pamphlet with clear sections.

Programme: {programme_title}
Based on: {course_name}
Duration: {weeks} weeks | Credits: {ects} ECTS
Mode: Online / Hybrid
University: Xamk (South-Eastern Finland University of Applied Sciences)
Schedule: {weekly_schedule(weekly_structure)}

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


def weekly_schedule(weekly_structure: dict) -> str:
    return "".join(
        f"\n{week}:\n" + "\n".join(f"  - {topic}" for topic in topics)
        for week, topics in weekly_structure.items()
    )
