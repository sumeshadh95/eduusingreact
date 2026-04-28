"""Plan-generation API routes."""

from fastapi import APIRouter, HTTPException

from api.bootstrap_payload import bootstrap_payload, selected_trend
from api.config import provider_status
from api.plan_builder import build_plan
from api.programme_actions import regenerate_programme_payload
from api.schemas import PlanPayload, ProgrammeRequest, TrendRequest
from api.summary_actions import regenerate_summary_payload

router = APIRouter()


@router.get("/status")
def status():
    return provider_status()


@router.get("/bootstrap")
def bootstrap():
    return bootstrap_payload()


@router.post("/plan")
def generate_plan(payload: TrendRequest):
    trend = selected_trend(payload.trend_name)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return build_plan(trend)


@router.post("/regenerate-summary")
def regenerate_summary(payload: PlanPayload):
    return regenerate_summary_payload(payload.plan)


@router.post("/regenerate-programme")
def regenerate_programme(payload: ProgrammeRequest):
    return regenerate_programme_payload(payload.plan, payload.approach)
