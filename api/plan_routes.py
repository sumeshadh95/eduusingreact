"""Plan-generation API routes."""

from fastapi import APIRouter, HTTPException

from api.config import effective_api_key, provider_status
from api.market import market_analysis
from api.plan_builder import build_plan, fallback_programme
from api.route_responses import programme_response
from api.schemas import PlanPayload, ProgrammeRequest, TrendRequest
from api.serializers import camel_personalized, snake_analysis, summary_card
from services import ai_service
from services import data_loader
from services import personalization

router = APIRouter()


@router.get("/status")
def status():
    return provider_status()


@router.get("/bootstrap")
def bootstrap():
    return {
        "trends": data_loader.load_trends(),
        "courses": data_loader.load_courses(),
        "teachers": data_loader.load_teachers(),
        "provider": provider_status(),
    }


@router.post("/plan")
def generate_plan(payload: TrendRequest):
    trend = selected_trend(payload.trend_name)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return build_plan(trend)


@router.post("/regenerate-summary")
def regenerate_summary(payload: PlanPayload):
    plan = payload.plan
    api_key = effective_api_key()
    course = plan.get("course", {})
    summary_text, used_fallback = ai_service.summarize(plan.get("materialText", ""), api_key=api_key)
    difficulty, difficulty_used_fallback = ai_service.analyze_course_difficulty(
        course,
        plan.get("materialText", ""),
        summary_text,
        api_key=api_key,
    )
    chapters, final_assignment, personalization_used_fallback = personalization.get_personalized_chapters(
        course.get("course_name", ""),
        "nursing",
        api_key=api_key,
    )
    return summary_response(
        plan,
        summary_text,
        used_fallback,
        difficulty,
        difficulty_used_fallback,
        (chapters, final_assignment, personalization_used_fallback),
    )


@router.post("/regenerate-programme")
def regenerate_programme(payload: ProgrammeRequest):
    plan = payload.plan
    api_key = effective_api_key()
    analysis = snake_analysis(plan.get("analysis", {}))
    programme, used_fallback = ai_service.generate_programme_content(
        plan.get("course", {}),
        plan.get("teacher", {}),
        plan.get("trend", {}),
        analysis["weeks"],
        analysis["ects"],
        plan.get("summary", {}).get("body", ""),
        api_key=api_key,
        approach=payload.approach.strip() or None,
    )
    if not programme or used_fallback:
        programme = fallback_programme(plan.get("course", {}), plan.get("teacher", {}), analysis)
        used_fallback = True
    return programme_response(programme, used_fallback)


def selected_trend(trend_name: str) -> dict | None:
    return next((item for item in data_loader.load_trends() if item.get("trend") == trend_name), None)


def summary_response(
    plan: dict,
    summary_text: str,
    summary_used_fallback: bool,
    difficulty: dict,
    difficulty_used_fallback: bool,
    personalized_result: tuple,
) -> dict:
    chapters, final_assignment, personalization_used_fallback = personalized_result
    course = plan.get("course", {})
    trend = plan.get("trend", {})
    analysis = snake_analysis(plan.get("analysis", {}))
    return {
        "summary": summary_card(summary_text, course, trend, analysis, plan.get("match", {})),
        "summaryUsedFallback": summary_used_fallback,
        "difficulty": {**difficulty, "usedFallback": difficulty_used_fallback},
        "market": market_analysis(course, trend),
        "personalized": camel_personalized(chapters, final_assignment, personalization_used_fallback),
        "message": ai_service.get_last_error(),
        "provider": provider_status(),
    }
