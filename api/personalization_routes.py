"""Personalized learning and minigame API routes."""

from fastapi import APIRouter

from api.config import effective_api_key, provider_status
from api.route_responses import failed_question_response
from api.schemas import PlanPayload, QuestionRequest
from api.serializers import camel_chapter, camel_personalized, snake_chapter
from services import ai_service
from services import personalization

router = APIRouter()


@router.post("/regenerate-personalization")
def regenerate_personalization(payload: PlanPayload):
    api_key = effective_api_key()
    course = payload.plan.get("course", {})
    chapters, final_assignment, used_fallback = personalization.get_personalized_chapters(
        course.get("course_name", ""),
        "nursing",
        api_key=api_key,
    )
    return {
        "personalized": camel_personalized(chapters, final_assignment, used_fallback),
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }


@router.post("/regenerate-question")
def regenerate_question(payload: QuestionRequest):
    api_key = effective_api_key()
    question, used_fallback = ai_service.generate_minigame_question(
        payload.course_name,
        payload.student_field,
        snake_chapter(payload.chapter),
        api_key=api_key,
    )
    if not question or used_fallback:
        return failed_question_response()
    chapter = dict(payload.chapter)
    chapter["game"] = camel_chapter({"minigame": question})["game"]
    return {
        "ok": True,
        "chapter": chapter,
        "message": f"Question regenerated with {provider_status()['name']}.",
        "provider": provider_status(),
    }
