"""Talent search and finance API routes."""

from fastapi import APIRouter

from api.schemas import PlanPayload
from api.serializers import camel_talent, snake_programme
from services import finance
from services import talent_search

router = APIRouter()


@router.post("/search-talent")
def search_talent(payload: PlanPayload):
    plan = payload.plan
    results, status_message = talent_search.search_probable_teachers(
        plan.get("course", {}),
        plan.get("trend", {}),
        snake_programme(plan.get("programme", {})),
        limit=5,
    )
    return {
        "talent": [camel_talent(candidate) for candidate in results],
        "talentStatus": status_message,
    }


@router.get("/finance")
def finance_estimate(students: int = 25, price: float = 450, costs: float = 4250):
    return finance.compute(students, price, costs)
