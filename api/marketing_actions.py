"""Marketing route actions."""

from api.config import effective_api_key
from api.route_responses import marketing_response
from api.serializers import snake_analysis, snake_programme
from services import ai_service
from services import marketing


def regenerate_marketing_payload(plan: dict) -> dict:
    programme = snake_programme(plan.get("programme", {}))
    analysis = snake_analysis(plan.get("analysis", {}))
    content, used_fallback = ai_service.generate_marketing_content(
        programme.get("title", ""),
        plan.get("course", {}).get("course_name", ""),
        analysis["weeks"],
        analysis["ects"],
        api_key=effective_api_key(),
    )
    if not content or used_fallback:
        content = marketing.get_marketing_content(programme)
        used_fallback = True
    return marketing_response(content, used_fallback)
