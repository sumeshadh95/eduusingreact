"""Request models used by the FastAPI routes."""

from typing import Any

from pydantic import BaseModel, Field


class TrendRequest(BaseModel):
    trend_name: str = Field(..., min_length=1)


class PlanPayload(BaseModel):
    plan: dict[str, Any]


class ProgrammeRequest(BaseModel):
    plan: dict[str, Any]
    approach: str = ""


class QuestionRequest(BaseModel):
    course_name: str = ""
    chapter: dict[str, Any]
    student_field: str = "nursing"


class ImageRequest(BaseModel):
    programme_title: str
    content: dict[str, Any]
    image_type: str


class RecruitmentEmailRequest(BaseModel):
    candidate: dict[str, Any]
    programme: dict[str, Any]
    course: dict[str, Any]


class BrochureRequest(BaseModel):
    programme: dict[str, Any]
    course: dict[str, Any]
    analysis: dict[str, Any]
