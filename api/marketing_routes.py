"""Marketing, image, brochure, and recruitment email API routes."""

from fastapi import APIRouter

from api.brochure_actions import generate_brochure_payload
from api.marketing_actions import regenerate_marketing_payload
from api.marketing_image_actions import generate_marketing_image_payload
from api.recruitment_actions import generate_recruitment_email_payload
from api.schemas import BrochureRequest, ImageRequest, PlanPayload, RecruitmentEmailRequest

router = APIRouter()


@router.post("/regenerate-marketing")
def regenerate_marketing(payload: PlanPayload):
    return regenerate_marketing_payload(payload.plan)


@router.post("/generate-marketing-image")
def generate_marketing_image(payload: ImageRequest):
    return generate_marketing_image_payload(payload.programme_title, payload.content, payload.image_type)


@router.post("/generate-brochure")
def generate_brochure(payload: BrochureRequest):
    return generate_brochure_payload(payload.programme, payload.course, payload.analysis)


@router.post("/generate-recruitment-email")
def generate_recruitment_email(payload: RecruitmentEmailRequest):
    return generate_recruitment_email_payload(payload.candidate, payload.programme, payload.course)
