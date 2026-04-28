"""
React API backend for CoursePilot AI.

The React app keeps the new UI. This file keeps the original Streamlit demo's
business behavior by wrapping the existing services/* modules and reading the
Gemini/OpenAI key from .env on the server side.
"""

import json
import os
import time
from io import BytesIO
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from services import ai_service
from services import course_generator
from services import data_loader
from services import finance
from services import marketing
from services import matcher
from services import material_analyzer
from services import personalization
from services import talent_search

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "generated_assets"

load_dotenv(BASE_DIR / ".env", override=True)

app = FastAPI(title="CoursePilot AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/generated_assets", StaticFiles(directory=ASSET_DIR), name="generated_assets")


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


def _effective_api_key() -> str:
    load_dotenv(BASE_DIR / ".env", override=True)
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
        or os.environ.get("OPENAI_API_KEY", "").strip()
    )


def _provider_status() -> dict[str, Any]:
    load_dotenv(BASE_DIR / ".env", override=True)
    provider_name = ai_service.get_active_provider_name(_effective_api_key())
    model_var = "GEMINI_MODEL" if provider_name == "Gemini" else "OPENAI_MODEL"
    return {
        "name": provider_name,
        "hasKey": bool(_effective_api_key()),
        "model": os.environ.get(model_var, "").strip(),
        "lastError": ai_service.get_last_error(),
    }


def _camel_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "size": analysis.get("size", ""),
        "weeks": analysis.get("weeks", 0),
        "ects": analysis.get("ects", 3),
        "wordCount": analysis.get("word_count", analysis.get("wordCount", 0)),
    }


def _snake_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "size": analysis.get("size", ""),
        "weeks": analysis.get("weeks", 0),
        "ects": analysis.get("ects", 3),
        "word_count": analysis.get("word_count", analysis.get("wordCount", 0)),
    }


def _load_market_courses() -> list[dict[str, Any]]:
    path = BASE_DIR / "data" / "market_courses.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _market_analysis(course: dict[str, Any], trend: dict[str, Any]) -> dict[str, Any]:
    market_sets = _load_market_courses()
    market_entry = next(
        (
            item
            for item in market_sets
            if item.get("course_id") == course.get("course_id")
            or item.get("trend", "").lower() == trend.get("trend", "").lower()
        ),
        {},
    )
    similar_courses = market_entry.get("courses", [])
    prices = [float(item.get("price_eur", 0)) for item in similar_courses if item.get("price_eur")]
    average_price = round(sum(prices) / len(prices)) if prices else 400
    recommended_price = round((average_price * 0.775) / 5) * 5
    recommended_price = min(max(recommended_price, 250), max(250, average_price - 50))
    range_low = max(199, recommended_price - 10)
    range_high = recommended_price + 5
    difference = average_price - recommended_price
    percent_saving = round((difference / average_price) * 100) if average_price else 0

    demand_counts: dict[str, int] = {}
    for item in similar_courses:
        demand = item.get("demand", "Medium")
        demand_counts[demand] = demand_counts.get(demand, 0) + 1
    demand_label = max(demand_counts, key=demand_counts.get) if demand_counts else "Medium"

    return {
        "similarCourses": similar_courses,
        "averageCompetitorPrice": average_price,
        "recommendedPrice": recommended_price,
        "recommendedRange": {"low": range_low, "high": range_high},
        "priceDifference": difference,
        "percentSaving": percent_saving,
        "demandLabel": demand_label,
        "positioning": (
            f"Comparable programmes cluster around EUR {average_price}. "
            f"A Xamk price near EUR {range_low}-{range_high} undercuts the market while preserving a premium academic signal."
        ),
        "comparisonRows": [
            {
                "provider": item.get("provider", ""),
                "title": item.get("title", ""),
                "platformPrice": item.get("price_eur", 0),
                "xamkPrice": recommended_price,
                "difference": item.get("price_eur", 0) - recommended_price,
                "format": item.get("format", ""),
                "demand": item.get("demand", ""),
            }
            for item in similar_courses
        ],
    }


def _camel_programme(programme: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": programme.get("title", ""),
        "basedOn": programme.get("based_on", programme.get("basedOn", "")),
        "ects": programme.get("ects", 3),
        "durationWeeks": programme.get("duration_weeks", programme.get("durationWeeks", 0)),
        "mode": programme.get("mode", ""),
        "teacher": programme.get("teacher", ""),
        "teacherId": programme.get("teacher_id", programme.get("teacherId", "")),
        "availableMonths": programme.get("available_months", programme.get("availableMonths", [])),
        "targetStudents": programme.get("target_students", programme.get("targetStudents", "")),
        "outcomes": programme.get("learning_outcomes", programme.get("outcomes", [])),
        "weeklyStructure": programme.get("weekly_structure", programme.get("weeklyStructure", {})),
        "assessment": programme.get("assessment", ""),
        "demoPitch": programme.get("demo_pitch", programme.get("demoPitch", "")),
    }


def _snake_programme(programme: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": programme.get("title", ""),
        "based_on": programme.get("based_on", programme.get("basedOn", "")),
        "ects": programme.get("ects", 3),
        "duration_weeks": programme.get("duration_weeks", programme.get("durationWeeks", 0)),
        "mode": programme.get("mode", ""),
        "teacher": programme.get("teacher", ""),
        "teacher_id": programme.get("teacher_id", programme.get("teacherId", "")),
        "available_months": programme.get("available_months", programme.get("availableMonths", [])),
        "target_students": programme.get("target_students", programme.get("targetStudents", "")),
        "learning_outcomes": programme.get("learning_outcomes", programme.get("outcomes", [])),
        "weekly_structure": programme.get("weekly_structure", programme.get("weeklyStructure", {})),
        "assessment": programme.get("assessment", ""),
        "demo_pitch": programme.get("demo_pitch", programme.get("demoPitch", "")),
    }


def _summary_card(summary_text: str, course: dict[str, Any], trend: dict[str, Any], analysis: dict[str, Any], match_result: dict[str, Any]) -> dict[str, Any]:
    keywords = match_result.get("matching_keywords", match_result.get("matchingKeywords", []))
    return {
        "title": f"{course.get('course_name', 'Course')} can become a {analysis.get('weeks', 0)}-week short programme",
        "body": summary_text,
        "highlights": [
            f"Trend fit is strongest around {', '.join(keywords[:4])}." if keywords else f"Trend fit is tied to {trend.get('trend', 'the selected topic')}.",
            f"The material maps to {analysis.get('ects', 3)} ECTS across {analysis.get('weeks', 0)} week(s).",
            "The AI output can be regenerated while keeping the source course and trend selection.",
        ],
    }


def _camel_chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    game = chapter.get("minigame", chapter.get("game", {})) or {}
    return {
        "title": chapter.get("title", ""),
        "standard": chapter.get("standard_explanation", chapter.get("standard", "")),
        "personalized": chapter.get("personalized_explanation", chapter.get("personalized", "")),
        "game": {
            "name": game.get("name", ""),
            "description": game.get("description", ""),
            "scenario": game.get("scenario", ""),
            "choices": game.get("choices", []),
            "correctChoice": game.get("correct_choice", game.get("correctChoice", "")),
            "feedback": game.get("feedback", ""),
        },
    }


def _snake_chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    game = chapter.get("minigame", chapter.get("game", {})) or {}
    return {
        "title": chapter.get("title", ""),
        "standard_explanation": chapter.get("standard_explanation", chapter.get("standard", "")),
        "personalized_explanation": chapter.get("personalized_explanation", chapter.get("personalized", "")),
        "minigame": {
            "name": game.get("name", ""),
            "description": game.get("description", ""),
            "scenario": game.get("scenario", ""),
            "choices": game.get("choices", []),
            "correct_choice": game.get("correct_choice", game.get("correctChoice", "")),
            "feedback": game.get("feedback", ""),
        },
    }


def _camel_personalized(chapters: list[dict[str, Any]], final_assignment: str, used_fallback: bool) -> dict[str, Any]:
    return {
        "studentProfile": "Nursing student interested in IT and electronics",
        "chapters": [_camel_chapter(chapter) for chapter in chapters],
        "finalAssignment": final_assignment,
        "usedFallback": used_fallback,
    }


def _camel_marketing(content: dict[str, Any], used_fallback: bool = False) -> dict[str, Any]:
    return {
        "website": content.get("website", ""),
        "social": content.get("social", ""),
        "email": content.get("email", ""),
        "tagline": content.get("tagline", ""),
        "sellingPoints": content.get("selling_points", content.get("sellingPoints", [])),
        "usedFallback": used_fallback,
    }


def _snake_marketing(content: dict[str, Any]) -> dict[str, Any]:
    return {
        "website": content.get("website", ""),
        "social": content.get("social", ""),
        "email": content.get("email", ""),
        "tagline": content.get("tagline", ""),
        "selling_points": content.get("selling_points", content.get("sellingPoints", [])),
    }


def _camel_talent(candidate: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(candidate)
    enriched["matchScore"] = candidate.get("match_score", candidate.get("matchScore", 0))
    enriched["matchReasons"] = candidate.get("match_reasons", candidate.get("matchReasons", []))
    return enriched


def _find_teacher(course: dict[str, Any], teachers: list[dict[str, Any]]) -> dict[str, Any]:
    teacher_id = course.get("teacher_id", "")
    return next((teacher for teacher in teachers if teacher.get("teacher_id") == teacher_id), teachers[0] if teachers else {})


def _fallback_programme(course: dict[str, Any], teacher: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    return course_generator.generate_programme(
        course,
        teacher,
        analysis.get("weeks", 2),
        analysis.get("ects", 3),
    )


def _build_plan(trend: dict[str, Any]) -> dict[str, Any]:
    api_key = _effective_api_key()
    courses = data_loader.load_courses()
    teachers = data_loader.load_teachers()

    match_result = matcher.match_trend_to_course(trend, courses)
    course = match_result.get("course") or (courses[0] if courses else {})
    material_text = data_loader.load_material(course.get("material_file", ""))
    analysis = material_analyzer.analyze(material_text)
    teacher = _find_teacher(course, teachers)

    summary_text, summary_used_fallback = ai_service.summarize(material_text, api_key=api_key)
    difficulty, difficulty_used_fallback = ai_service.analyze_course_difficulty(
        course,
        material_text,
        summary_text,
        api_key=api_key,
    )
    programme, programme_used_fallback = ai_service.generate_programme_content(
        course,
        teacher,
        trend,
        analysis["weeks"],
        analysis["ects"],
        summary_text,
        api_key=api_key,
    )
    if not programme or programme_used_fallback:
        programme = _fallback_programme(course, teacher, analysis)
        programme_used_fallback = True

    chapters, final_assignment, personalization_used_fallback = personalization.get_personalized_chapters(
        course.get("course_name", ""),
        "nursing",
        api_key=api_key,
    )

    marketing_content, marketing_used_fallback = ai_service.generate_marketing_content(
        programme.get("title", ""),
        course.get("course_name", ""),
        analysis["weeks"],
        analysis["ects"],
        api_key=api_key,
    )
    if not marketing_content or marketing_used_fallback:
        marketing_content = marketing.get_marketing_content(programme)
        marketing_used_fallback = True

    talent_results, talent_status = talent_search.search_probable_teachers(course, trend, programme, limit=5)

    return {
        "trend": trend,
        "match": {
            "score": match_result.get("score", 0),
            "matchingKeywords": match_result.get("matching_keywords", []),
            "reason": match_result.get("reason", ""),
        },
        "course": course,
        "materialText": material_text,
        "analysis": _camel_analysis(analysis),
        "teacher": teacher,
        "teachers": teachers,
        "summary": _summary_card(summary_text, course, trend, analysis, match_result),
        "summaryUsedFallback": summary_used_fallback,
        "difficulty": {
            **difficulty,
            "usedFallback": difficulty_used_fallback,
        },
        "market": _market_analysis(course, trend),
        "programme": _camel_programme(programme),
        "programmeUsedFallback": programme_used_fallback,
        "personalized": _camel_personalized(chapters, final_assignment, personalization_used_fallback),
        "marketing": _camel_marketing(marketing_content, marketing_used_fallback),
        "talent": [_camel_talent(candidate) for candidate in talent_results],
        "talentStatus": talent_status,
        "provider": _provider_status(),
    }


def _load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _draw_xamk_logo(draw, x: int, y: int, scale: int = 1):
    logo_font = _load_font(34 * scale, bold=True)
    sub_font = _load_font(12 * scale, bold=False)
    draw.rounded_rectangle((x, y, x + 168 * scale, y + 58 * scale), radius=12 * scale, fill="#ffffff")
    draw.rectangle((x + 14 * scale, y + 13 * scale, x + 30 * scale, y + 45 * scale), fill="#00a651")
    draw.text((x + 40 * scale, y + 7 * scale), "Xamk", font=logo_font, fill="#003b5c")
    draw.text((x + 41 * scale, y + 42 * scale), "South-Eastern Finland UAS", font=sub_font, fill="#64748b")


def _apply_xamk_branding(image_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    try:
        from PIL import Image, ImageDraw

        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(image)
        scale = max(1, round(image.width / 1000))
        margin = max(28, image.width // 24)
        _draw_xamk_logo(draw, margin, margin, scale=scale)

        footer_font = _load_font(max(18, image.width // 46), bold=True)
        footer_text = "Xamk Continuing Education"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        pad_x = max(18, image.width // 70)
        pad_y = max(10, image.width // 110)
        x2 = image.width - margin
        y2 = image.height - margin
        draw.rounded_rectangle(
            (x2 - footer_width - (pad_x * 2), y2 - footer_font.size - (pad_y * 2), x2, y2),
            radius=max(12, image.width // 90),
            fill="#003b5c",
        )
        draw.text(
            (x2 - footer_width - pad_x, y2 - footer_font.size - pad_y - 2),
            footer_text,
            font=footer_font,
            fill="#ffffff",
        )

        output = BytesIO()
        image.save(output, "PNG")
        return (output.getvalue(), "image/png")
    except Exception:
        return (image_bytes, mime_type or "image/png")


def _save_generated_image(image_bytes: bytes, mime_type: str, prefix: str) -> str:
    ASSET_DIR.mkdir(exist_ok=True)
    branded_bytes, branded_mime = _apply_xamk_branding(image_bytes, mime_type)
    ext = ".jpg" if "jpeg" in (branded_mime or "").lower() else ".png"
    filename = f"{prefix}_{int(time.time())}{ext}"
    path = ASSET_DIR / filename
    path.write_bytes(branded_bytes)
    return f"/generated_assets/{filename}"


@app.get("/api/status")
def status():
    return _provider_status()


@app.get("/api/bootstrap")
def bootstrap():
    return {
        "trends": data_loader.load_trends(),
        "courses": data_loader.load_courses(),
        "teachers": data_loader.load_teachers(),
        "provider": _provider_status(),
    }


@app.post("/api/plan")
def generate_plan(payload: TrendRequest):
    trends = data_loader.load_trends()
    trend = next((item for item in trends if item.get("trend") == payload.trend_name), None)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return _build_plan(trend)


@app.post("/api/regenerate-summary")
def regenerate_summary(payload: PlanPayload):
    plan = payload.plan
    api_key = _effective_api_key()
    summary_text, used_fallback = ai_service.summarize(plan.get("materialText", ""), api_key=api_key)
    course = plan.get("course", {})
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
    return {
        "summary": _summary_card(summary_text, course, plan.get("trend", {}), _snake_analysis(plan.get("analysis", {})), plan.get("match", {})),
        "summaryUsedFallback": used_fallback,
        "difficulty": {
            **difficulty,
            "usedFallback": difficulty_used_fallback,
        },
        "market": _market_analysis(course, plan.get("trend", {})),
        "personalized": _camel_personalized(chapters, final_assignment, personalization_used_fallback),
        "message": ai_service.get_last_error(),
        "provider": _provider_status(),
    }


@app.post("/api/regenerate-programme")
def regenerate_programme(payload: ProgrammeRequest):
    plan = payload.plan
    api_key = _effective_api_key()
    analysis = _snake_analysis(plan.get("analysis", {}))
    summary = plan.get("summary", {}).get("body", "")
    programme, used_fallback = ai_service.generate_programme_content(
        plan.get("course", {}),
        plan.get("teacher", {}),
        plan.get("trend", {}),
        analysis["weeks"],
        analysis["ects"],
        summary,
        api_key=api_key,
        approach=payload.approach.strip() or None,
    )
    if not programme or used_fallback:
        programme = _fallback_programme(plan.get("course", {}), plan.get("teacher", {}), analysis)
        used_fallback = True
    return {
        "programme": _camel_programme(programme),
        "programmeUsedFallback": used_fallback,
        "message": ai_service.get_last_error(),
        "provider": _provider_status(),
    }


@app.post("/api/regenerate-personalization")
def regenerate_personalization(payload: PlanPayload):
    api_key = _effective_api_key()
    course = payload.plan.get("course", {})
    chapters, final_assignment, used_fallback = personalization.get_personalized_chapters(
        course.get("course_name", ""),
        "nursing",
        api_key=api_key,
    )
    return {
        "personalized": _camel_personalized(chapters, final_assignment, used_fallback),
        "message": ai_service.get_last_error(),
        "provider": _provider_status(),
    }


@app.post("/api/regenerate-question")
def regenerate_question(payload: QuestionRequest):
    api_key = _effective_api_key()
    question, used_fallback = ai_service.generate_minigame_question(
        payload.course_name,
        payload.student_field,
        _snake_chapter(payload.chapter),
        api_key=api_key,
    )
    if not question or used_fallback:
        return {
            "ok": False,
            "message": ai_service.get_last_error() or "Question regeneration did not return a usable question.",
            "provider": _provider_status(),
        }
    chapter = dict(payload.chapter)
    chapter["game"] = _camel_chapter({"minigame": question})["game"]
    return {
        "ok": True,
        "chapter": chapter,
        "message": f"Question regenerated with {_provider_status()['name']}.",
        "provider": _provider_status(),
    }


@app.post("/api/regenerate-marketing")
def regenerate_marketing(payload: PlanPayload):
    plan = payload.plan
    api_key = _effective_api_key()
    programme = _snake_programme(plan.get("programme", {}))
    analysis = _snake_analysis(plan.get("analysis", {}))
    course = plan.get("course", {})
    content, used_fallback = ai_service.generate_marketing_content(
        programme.get("title", ""),
        course.get("course_name", ""),
        analysis["weeks"],
        analysis["ects"],
        api_key=api_key,
    )
    if not content or used_fallback:
        content = marketing.get_marketing_content(programme)
        used_fallback = True
    return {
        "marketing": _camel_marketing(content, used_fallback),
        "message": ai_service.get_last_error(),
        "provider": _provider_status(),
    }


@app.post("/api/generate-marketing-image")
def generate_marketing_image(payload: ImageRequest):
    api_key = _effective_api_key()
    image_bytes, mime_type, used_fallback = ai_service.generate_marketing_image(
        payload.programme_title,
        _snake_marketing(payload.content),
        payload.image_type,
        api_key=api_key,
    )
    if not image_bytes or used_fallback:
        return {
            "ok": False,
            "message": ai_service.get_last_error() or "Gemini did not return image data.",
            "provider": _provider_status(),
        }
    return {
        "ok": True,
        "imageType": payload.image_type,
        "imageUrl": _save_generated_image(image_bytes, mime_type, payload.image_type),
        "message": f"{payload.image_type.title()} image generated with {_provider_status()['name']}.",
        "provider": _provider_status(),
    }


@app.post("/api/generate-brochure")
def generate_brochure(payload: BrochureRequest):
    api_key = _effective_api_key()
    programme = _snake_programme(payload.programme)
    analysis = _snake_analysis(payload.analysis)
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
        "provider": _provider_status(),
    }


@app.post("/api/search-talent")
def search_talent(payload: PlanPayload):
    plan = payload.plan
    results, status_message = talent_search.search_probable_teachers(
        plan.get("course", {}),
        plan.get("trend", {}),
        _snake_programme(plan.get("programme", {})),
        limit=5,
    )
    return {
        "talent": [_camel_talent(candidate) for candidate in results],
        "talentStatus": status_message,
    }


@app.post("/api/generate-recruitment-email")
def generate_recruitment_email(payload: RecruitmentEmailRequest):
    api_key = _effective_api_key()
    email, used_fallback = ai_service.generate_recruitment_email(
        payload.candidate,
        _snake_programme(payload.programme),
        payload.course,
        api_key=api_key,
    )
    return {
        "email": email,
        "usedFallback": used_fallback,
        "message": ai_service.get_last_error(),
        "provider": _provider_status(),
    }


@app.get("/api/finance")
def finance_estimate(students: int = 25, price: float = 450, costs: float = 4250):
    return finance.compute(students, price, costs)
