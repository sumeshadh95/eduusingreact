"""Marketing, image, brochure, and recruitment email API routes."""

from fastapi import APIRouter

from api.config import effective_api_key, provider_status
from api.image_assets import save_generated_image
from api.route_responses import failed_image_response, marketing_response
from api.schemas import BrochureRequest, ImageRequest, PlanPayload, RecruitmentEmailRequest
from api.serializers import snake_analysis, snake_marketing, snake_programme
from services import ai_service
from services import marketing

router = APIRouter()


@router.post("/regenerate-marketing")
def regenerate_marketing(payload: PlanPayload):
    plan = payload.plan
    api_key = effective_api_key()
    programme = snake_programme(plan.get("programme", {}))
    analysis = snake_analysis(plan.get("analysis", {}))
    content, used_fallback = ai_service.generate_marketing_content(
        programme.get("title", ""),
        plan.get("course", {}).get("course_name", ""),
        analysis["weeks"],
        analysis["ects"],
        api_key=api_key,
    )
    if not content or used_fallback:
        content = marketing.get_marketing_content(programme)
        used_fallback = True
    return marketing_response(content, used_fallback)


@router.post("/generate-marketing-image")
def generate_marketing_image(payload: ImageRequest):
    api_key = effective_api_key()
    image_bytes, mime_type, used_fallback = ai_service.generate_marketing_image(
        payload.programme_title,
        snake_marketing(payload.content),
        payload.image_type,
        api_key=api_key,
    )
    if not image_bytes or used_fallback:
        return failed_image_response()
    return {
        "ok": True,
        "imageType": payload.image_type,
        "imageUrl": save_generated_image(image_bytes, mime_type, payload.image_type),
        "message": f"{payload.image_type.title()} image generated with {provider_status()['name']}.",
        "provider": provider_status(),
    }


@router.post("/generate-brochure")
def generate_brochure(payload: BrochureRequest):
    api_key = effective_api_key()
    programme = snake_programme(payload.programme)
    analysis = snake_analysis(payload.analysis)
    brochure, used_fallback = ai_service.generate_brochure(
        programme.get("title", ""),
        payload.course.get("course_name", ""),
        analysis["weeks"],
        analysis["ects"],
        programme.get("weekly_structure", {}),
        api_key=api_key,
    )
    return {
        "ok": bool(brochure and not used_fallback),
        "brochure": brochure or "",
        "usedFallback": used_fallback,
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }


@router.post("/generate-recruitment-email")
def generate_recruitment_email(payload: RecruitmentEmailRequest):
    api_key = effective_api_key()
    email, used_fallback = ai_service.generate_recruitment_email(
        payload.candidate,
        snake_programme(payload.programme),
        payload.course,
        api_key=api_key,
    )
    return {
        "email": email,
        "usedFallback": used_fallback,
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }
