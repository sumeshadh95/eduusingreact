"""Top-level CoursePilot API router."""

from fastapi import APIRouter

from api.marketing_routes import router as marketing_router
from api.personalization_routes import router as personalization_router
from api.plan_routes import router as plan_router
from api.talent_routes import router as talent_router

router = APIRouter(prefix="/api")
router.include_router(plan_router)
router.include_router(personalization_router)
router.include_router(marketing_router)
router.include_router(talent_router)
