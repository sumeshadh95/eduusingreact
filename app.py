"""
CoursePilot AI — Streamlit demo app.

This is the ONLY file that imports streamlit and touches st.session_state.
All business logic lives in services/*.
"""

import os
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from services import data_loader
from services import matcher
from services import material_analyzer
from services import ai_service
from services import course_generator
from services import personalization
from services import marketing
from services import talent_search
from services import finance

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv(override=True)

ASSET_DIR = Path(__file__).parent / "generated_assets"

st.set_page_config(
    page_title="CoursePilot AI",
    page_icon="🎓",
    layout="wide",
)


# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

def inject_css():
    st.markdown(
        """
        <style>
        .block-container { padding-top: 2rem; }
        :root {
            --primary-blue: #1d4ed8;
            --light-blue-bg: #e8f0ff;
            --page-bg: #f7f9fc;
            --success-green: #065f46;
            --green-bg: #ecfdf5;
        }
        .trend-card {
            background: #ffffff;
            border: 1px solid #e3e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 12px;
            transition: box-shadow 0.2s;
        }
        .trend-card-selected {
            background: #ffffff;
            border: 2px solid #1d4ed8;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 12px;
            box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.15);
        }
        .badge-trending {
            display: inline-block;
            background: #d1fae5;
            color: #065f46;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
        }
        .badge-rising {
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
        }
        .chip {
            display: inline-block;
            background: #eef2ff;
            color: #3730a3;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            margin: 3px 2px;
            font-weight: 500;
        }
        .info-card {
            background: #ffffff;
            border: 1px solid #e3e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 12px;
        }
        .chapter-card {
            background: #ffffff;
            border: 1px solid #e3e8f0;
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 18px;
        }
        .chapter-card h4 {
            color: #1d4ed8;
            margin-top: 0;
        }
        .chapter-label {
            font-size: 11px;
            font-weight: 700;
            color: #5a6b8c;
            text-transform: uppercase;
            margin-top: 14px;
            margin-bottom: 4px;
        }
        .minigame-card {
            background: #ecfdf5;
            border: 1px solid #6ee7b7;
            border-radius: 10px;
            padding: 14px 16px;
            margin-top: 12px;
        }
        .minigame-card .mg-name {
            font-weight: 700;
            color: #065f46;
        }
        .play-card {
            background: #f8fafc;
            border: 1px solid #d8e0ea;
            border-radius: 10px;
            padding: 14px 16px;
            margin-top: 10px;
        }
        .ai-note {
            color: #475569;
            font-size: 13px;
            margin: 4px 0 14px;
        }
        .visual-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
        }
        .section-title {
            font-size: 26px;
            font-weight: 700;
            color: #1a2b4a;
            margin-bottom: 8px;
        }
        .nursing-banner {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .success-banner {
            background: #ecfdf5;
            border-left: 4px solid #10b981;
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 16px;
            color: #065f46;
            font-weight: 500;
        }
        .detail-item { margin-bottom: 6px; }
        .detail-label {
            font-weight: 600;
            color: #5a6b8c;
            font-size: 13px;
        }
        .locked-msg {
            background: #f7f9fc;
            border: 1px dashed #cbd5e1;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            color: #64748b;
            font-size: 16px;
            margin-top: 40px;
        }
        .api-status-ok {
            color: #065f46;
            font-size: 12px;
            font-weight: 600;
        }
        .api-status-no {
            color: #dc2626;
            font-size: 12px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def _get_effective_api_key() -> str:
    """Return the active AI API key from .env."""
    load_dotenv(override=True)
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
        or os.environ.get("OPENAI_API_KEY", "").strip()
    )


def _get_active_provider_name() -> str:
    """Return the provider label shown in the UI."""
    load_dotenv(override=True)
    if os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip():
        return "Gemini"
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "OpenAI"
    return "AI"


def init_state():
    defaults = {
        "plan_generated": False,
        "trend": None,
        "trends": [],
        "course": None,
        "teacher": None,
        "match_result": None,
        "analysis": None,
        "summary": None,
        "summary_used_fallback": None,
        "programme": None,
        "programme_used_fallback": None,
        "programme_regen_status": None,
        "programme_regen_message": None,
        "material_text": None,
        "data_loaded": False,
        "data_error": False,
        "selected_trend_name": None,
        "personalized_chapters": None,
        "personalized_final_assignment": None,
        "personalization_used_fallback": None,
        "personalization_regen_status": None,
        "personalization_regen_message": None,
        "question_regen_messages": {},
        "pending_question_sync": None,
        "marketing_content": None,
        "marketing_used_fallback": None,
        "brochure_text": None,
        "marketing_image_paths": {},
        "marketing_image_status": None,
        "marketing_image_message": None,
        "talent_results": None,
        "talent_search_status": None,
        "recruitment_emails": {},
        "summary_regen_status": None,
        "summary_regen_message": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _fallback_programme(course: dict, teacher: dict, analysis: dict) -> dict:
    return course_generator.generate_programme(
        course,
        teacher,
        analysis["weeks"],
        analysis["ects"],
    )


def _generate_programme_with_ai(api_key: str) -> bool:
    """Populate session state with an AI-generated programme when possible."""
    programme, used_fallback = ai_service.generate_programme_content(
        st.session_state.course,
        st.session_state.teacher,
        st.session_state.trend,
        st.session_state.analysis["weeks"],
        st.session_state.analysis["ects"],
        st.session_state.summary or "",
        api_key=api_key,
    )
    if programme and not used_fallback:
        st.session_state.programme = programme
        st.session_state.programme_used_fallback = False
        return True

    st.session_state.programme = _fallback_programme(
        st.session_state.course,
        st.session_state.teacher,
        st.session_state.analysis,
    )
    st.session_state.programme_used_fallback = True
    return False


def _regenerate_personalized_learning(api_key: str) -> bool:
    chapters, final_assignment, p_fallback = personalization.get_personalized_chapters(
        st.session_state.course.get("course_name", ""),
        "nursing",
        api_key=api_key,
    )
    st.session_state.personalized_chapters = chapters
    st.session_state.personalized_final_assignment = final_assignment
    st.session_state.personalization_used_fallback = p_fallback
    for idx, chapter in enumerate(chapters):
        _prime_chapter_editor_state(idx, chapter, force=True)
    st.session_state["final_assignment_editor"] = final_assignment
    return not p_fallback


def _is_blank(value) -> bool:
    return not str(value or "").strip()


def _keep_existing_when_blank(current, edited):
    return edited if not _is_blank(edited) else (current or "")


def _apply_editor_state_to_chapter(idx: int, chapter: dict) -> dict:
    """Preserve non-empty admin edits before a question-only regeneration."""
    game = dict(chapter.get("minigame", {}) or {})
    text_fields = {
        "title": f"ch_title_{idx}",
        "standard_explanation": f"ch_standard_{idx}",
        "personalized_explanation": f"ch_personalized_{idx}",
    }
    game_fields = {
        "name": f"game_name_admin_{idx}",
        "description": f"game_description_admin_{idx}",
        "scenario": f"game_scenario_admin_{idx}",
        "feedback": f"game_feedback_admin_{idx}",
    }
    for field, key in text_fields.items():
        value = st.session_state.get(key)
        if not _is_blank(value):
            chapter[field] = value
    for field, key in game_fields.items():
        value = st.session_state.get(key)
        if not _is_blank(value):
            game[field] = value

    choices_text = st.session_state.get(f"game_choices_text_{idx}", "")
    choices = [line.strip() for line in choices_text.splitlines() if line.strip()]
    if choices:
        game["choices"] = choices
        correct = (
            st.session_state.get(f"game_correct_choice_editor_{idx}")
            or st.session_state.get(f"game_correct_choice_{idx}")
        )
        game["correct_choice"] = correct if correct in choices else choices[0]

    chapter["minigame"] = game
    return chapter


def _fallback_chapter_copy(idx: int, chapter: dict) -> dict:
    course_name = (st.session_state.course or {}).get("course_name", "the course")
    game = chapter.get("minigame", {}) or {}
    game_name = game.get("name") or "Applied Practice Challenge"
    scenario = game.get("scenario") or game.get("description") or "a practical student decision challenge"
    return {
        "title": chapter.get("title") or f"Chapter {idx + 1} - {game_name}",
        "standard_explanation": chapter.get("standard_explanation") or (
            f"This chapter connects {course_name} concepts to a practical learning activity. "
            "Students review the core idea, compare possible actions, and apply the concept in a short interactive scenario."
        ),
        "personalized_explanation": chapter.get("personalized_explanation") or (
            f"For a nursing student, this topic is framed around clinical judgement, patient safety, "
            f"and care-team communication through {scenario}."
        ),
    }


def _repair_blank_chapter_copy(idx: int, chapter: dict, api_key: str = None) -> dict:
    required = ["title", "standard_explanation", "personalized_explanation"]
    if all(not _is_blank(chapter.get(field)) for field in required):
        return chapter

    if api_key:
        patch, used_fallback = ai_service.generate_chapter_text_patch(
            (st.session_state.course or {}).get("course_name", ""),
            "nursing",
            chapter,
            api_key=api_key,
        )
        if patch and not used_fallback:
            for field in required:
                if _is_blank(chapter.get(field)) and not _is_blank(patch.get(field)):
                    chapter[field] = patch[field]

    fallback = _fallback_chapter_copy(idx, chapter)
    for field in required:
        if _is_blank(chapter.get(field)):
            chapter[field] = fallback[field]
    return chapter


def _prime_chapter_editor_state(idx: int, chapter: dict, force: bool = False):
    game = chapter.get("minigame", {}) or {}
    values = {
        f"ch_title_{idx}": chapter.get("title", ""),
        f"ch_standard_{idx}": chapter.get("standard_explanation", ""),
        f"ch_personalized_{idx}": chapter.get("personalized_explanation", ""),
        f"game_name_admin_{idx}": game.get("name", ""),
        f"game_description_admin_{idx}": game.get("description", ""),
        f"game_scenario_admin_{idx}": game.get("scenario", ""),
        f"game_choices_text_{idx}": "\n".join(game.get("choices", [])),
        f"game_feedback_admin_{idx}": game.get("feedback", ""),
    }
    for key, value in values.items():
        current = st.session_state.get(key)
        if key not in st.session_state or (force and not _is_blank(value)) or (_is_blank(current) and not _is_blank(value)):
            st.session_state[key] = value

    choices_text = st.session_state.get(f"game_choices_text_{idx}", values[f"game_choices_text_{idx}"])
    choices = [line.strip() for line in choices_text.splitlines() if line.strip()]
    if choices and force:
        st.session_state.pop(f"game_correct_choice_editor_{idx}", None)


def _regenerate_single_question(chapter_index: int, api_key: str) -> bool:
    chapters = list(st.session_state.personalized_chapters or [])
    if chapter_index >= len(chapters):
        return False
    chapters[chapter_index] = _apply_editor_state_to_chapter(chapter_index, chapters[chapter_index])
    question, used_fallback = ai_service.generate_minigame_question(
        st.session_state.course.get("course_name", ""),
        "nursing",
        chapters[chapter_index],
        api_key=api_key,
    )
    messages = dict(st.session_state.question_regen_messages or {})
    if question and not used_fallback:
        chapters[chapter_index]["minigame"] = question
        chapters[chapter_index] = _repair_blank_chapter_copy(chapter_index, chapters[chapter_index], api_key=api_key)
        st.session_state.personalized_chapters = chapters
        st.session_state.pending_question_sync = chapter_index
        messages[chapter_index] = {
            "status": "success",
            "text": f"Question regenerated with {_get_active_provider_name()}.",
        }
        st.session_state.question_regen_messages = messages
        return True

    messages[chapter_index] = {
        "status": "error",
        "text": ai_service.get_last_error() or "Question regeneration did not return a usable question.",
    }
    st.session_state.question_regen_messages = messages
    return False


def _save_generated_image(image_bytes: bytes, mime_type: str, prefix: str) -> str:
    ASSET_DIR.mkdir(exist_ok=True)
    image_bytes, mime_type = _apply_xamk_branding_to_ai_image(image_bytes, mime_type, prefix)
    ext = ".jpg" if "jpeg" in (mime_type or "").lower() else ".png"
    filename = f"{prefix}_{int(time.time())}{ext}"
    path = ASSET_DIR / filename
    path.write_bytes(image_bytes)
    return str(path)


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


def _wrap_text(draw, text: str, font, max_width: int) -> list:
    words = (text or "").split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_xamk_logo(draw, x: int, y: int, scale: int = 1):
    """Draw a compact Xamk-style wordmark for generated demo visuals."""
    logo_font = _load_font(34 * scale, bold=True)
    sub_font = _load_font(12 * scale, bold=False)
    draw.rounded_rectangle((x, y, x + 168 * scale, y + 58 * scale), radius=12 * scale, fill="#ffffff")
    draw.rectangle((x + 14 * scale, y + 13 * scale, x + 30 * scale, y + 45 * scale), fill="#00a651")
    draw.text((x + 40 * scale, y + 7 * scale), "Xamk", font=logo_font, fill="#003b5c")
    draw.text((x + 41 * scale, y + 42 * scale), "South-Eastern Finland UAS", font=sub_font, fill="#64748b")


def _apply_xamk_branding_to_ai_image(image_bytes: bytes, mime_type: str, image_type: str) -> tuple:
    """Add a crisp Xamk brand mark to a real AI-generated image."""
    try:
        from io import BytesIO

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


def _content_keywords() -> list:
    prog = st.session_state.programme or {}
    course = st.session_state.course or {}
    trend = st.session_state.trend or {}
    words = []
    for value in [
        course.get("course_name", ""),
        trend.get("trend", ""),
        prog.get("title", ""),
    ]:
        for token in value.replace("/", " ").replace("-", " ").split():
            token = token.strip(".,:;()[]")
            if len(token) > 3:
                words.append(token)
    for keyword in trend.get("keywords", []):
        words.append(keyword)
    for topics in prog.get("weekly_structure", {}).values():
        for topic in topics[:2]:
            label = topic.split("-")[0].split("—")[0].strip()
            if label:
                words.append(label)
    unique = []
    for word in words:
        if word.lower() not in [item.lower() for item in unique]:
            unique.append(word)
    return unique[:8]


def _create_demo_marketing_visual(image_type: str) -> str:
    """Create a fresh Xamk-branded visual from current course/programme content."""
    from PIL import Image, ImageDraw

    content = st.session_state.marketing_content or {}
    prog = st.session_state.programme or {}
    course = st.session_state.course or {}
    trend = st.session_state.trend or {}
    title = prog.get("title", "Game Development Winter Sprint")
    tagline = content.get("tagline", "Build your first playable prototype.")
    course_name = course.get("course_name", "Game Development")
    trend_name = trend.get("trend", "Creative Technology")
    keywords = _content_keywords()
    weeks = prog.get("duration_weeks", st.session_state.analysis.get("weeks", 2))
    ects = prog.get("ects", st.session_state.analysis.get("ects", 3))

    is_social = image_type == "social"
    width, height = (1080, 1080) if is_social else (1200, 1600)
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)

    # Structured Xamk-style background generated fresh on each click.
    for y in range(height):
        blend = y / max(height - 1, 1)
        r = int(245 * (1 - blend) + 226 * blend)
        g = int(250 * (1 - blend) + 246 * blend)
        b = int(252 * (1 - blend) + 254 * blend)
        draw.line((0, y, width, y), fill=(r, g, b))

    palette = [
        ("#003b5c", "#00a651", "#dbeafe"),
        ("#14315f", "#00a676", "#bfdbfe"),
        ("#102a43", "#009b72", "#c7d2fe"),
    ]
    accent, green, soft = palette[int(time.time()) % len(palette)]
    ink = "#111827"
    muted = "#475569"
    draw.rounded_rectangle((56, 56, width - 56, height - 56), radius=28, outline="#cbd5e1", width=3)
    draw.rectangle((0, height - 230, width, height), fill="#0f172a")
    draw.polygon([(width - 380, 0), (width, 0), (width, 380)], fill=soft)
    draw.polygon([(0, height - 440), (0, height), (440, height)], fill="#dcfce7")
    _draw_xamk_logo(draw, 88, 88, scale=1)

    motif_y = 210 if is_social else 250
    chip_font = _load_font(22, bold=True)
    for i, keyword in enumerate(keywords[:5]):
        x = 88 + (i % 3) * 285
        y = motif_y + (i // 3) * 92
        draw.rounded_rectangle((x, y, x + 245, y + 62), radius=16, fill="#ffffff", outline="#bfdbfe", width=2)
        draw.rectangle((x + 18, y + 18, x + 42, y + 42), fill=green if i % 2 else accent)
        draw.text((x + 56, y + 17), keyword[:19], font=chip_font, fill=ink)

    for i in range(6):
        x = width - 445 + i * 50
        draw.line((x, 430, x + 86, 520), fill="#93c5fd", width=5)
        draw.ellipse((x + 70, 500, x + 110, 540), fill=green)

    title_font = _load_font(62 if is_social else 68, bold=True)
    subtitle_font = _load_font(34 if is_social else 40, bold=False)
    label_font = _load_font(28 if is_social else 32, bold=True)
    small_font = _load_font(24 if is_social else 28, bold=False)

    y = 480 if is_social else 620
    draw.text((88, y - 86), f"{trend_name} • {course_name}", font=label_font, fill=green)
    title_width = width - (220 if is_social else 380)
    for line in _wrap_text(draw, title, title_font, title_width)[:3]:
        draw.text((88, y), line, font=title_font, fill=ink)
        y += title_font.size + 10
    y += 24
    for line in _wrap_text(draw, tagline, subtitle_font, width - 176)[:3]:
        draw.text((88, y), line, font=subtitle_font, fill=muted)
        y += subtitle_font.size + 8

    pill_y = height - 170
    pills = [f"{weeks} weeks", f"{ects} ECTS", "Online / Hybrid", "Prototype-first"]
    x = 88
    for pill in pills:
        text_width = draw.textbbox((0, 0), pill, font=small_font)[2]
        draw.rounded_rectangle((x, pill_y, x + text_width + 42, pill_y + 54), radius=27, fill="#ffffff")
        draw.text((x + 21, pill_y + 10), pill, font=small_font, fill=ink)
        x += text_width + 60

    footer = "Generated for CoursePilot AI demo"
    draw.text((88, height - 86), footer, font=small_font, fill="#e2e8f0")

    ASSET_DIR.mkdir(exist_ok=True)
    path = ASSET_DIR / f"{image_type}_designed_{int(time.time())}.png"
    image.save(path, "PNG")
    return str(path)


def _generate_marketing_visual(image_type: str):
    api_key = _get_effective_api_key()
    prog = st.session_state.programme
    content = st.session_state.marketing_content or {}
    image_bytes, mime_type, used_fallback = ai_service.generate_marketing_image(
        prog.get("title", ""),
        content,
        image_type,
        api_key=api_key,
    )
    if image_bytes and not used_fallback:
        path = _save_generated_image(image_bytes, mime_type, image_type)
        image_paths = dict(st.session_state.marketing_image_paths or {})
        image_paths[image_type] = path
        st.session_state.marketing_image_paths = image_paths
        st.session_state.marketing_image_status = "success"
        st.session_state.marketing_image_message = (
            f"{image_type.title()} image generated with {_get_active_provider_name()}."
        )
        return True

    image_paths = dict(st.session_state.marketing_image_paths or {})
    image_paths.pop(image_type, None)
    st.session_state.marketing_image_paths = image_paths
    st.session_state.marketing_image_status = "error"
    st.session_state.marketing_image_message = (
        ai_service.get_last_error()
        or "Gemini did not return image data. Check that this API key has image-generation access."
    )
    return False


def _search_teacher_talents():
    results, status = talent_search.search_probable_teachers(
        st.session_state.course or {},
        st.session_state.trend or {},
        st.session_state.programme or {},
        limit=5,
    )
    st.session_state.talent_results = results
    st.session_state.talent_search_status = status


def _generate_recruitment_email(candidate: dict) -> str:
    api_key = _get_effective_api_key()
    email, used_fallback = ai_service.generate_recruitment_email(
        candidate,
        st.session_state.programme or {},
        st.session_state.course or {},
        api_key=api_key,
    )
    emails = dict(st.session_state.recruitment_emails or {})
    emails[candidate.get("talent_id", candidate.get("name", ""))] = {
        "text": email,
        "used_fallback": used_fallback,
    }
    st.session_state.recruitment_emails = emails
    return email


# ---------------------------------------------------------------------------
# Cached data loading
# ---------------------------------------------------------------------------

@st.cache_data
def cached_load_trends():
    return data_loader.load_trends()

@st.cache_data
def cached_load_courses():
    return data_loader.load_courses()

@st.cache_data
def cached_load_teachers():
    return data_loader.load_teachers()

@st.cache_data
def cached_load_material(filename):
    return data_loader.load_material(filename)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

SECTION_LABELS = [
    "1. Home",
    "2. Course Match",
    "3. AI Summary",
    "4. Programme",
    "5. Personalized Learning",
    "6. Teacher",
    "7. Marketing",
    "8. Income",
]


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("### 🎓 CoursePilot AI")
        st.markdown("---")

        # API key status from .env only
        env_key = _get_effective_api_key()
        provider_name = _get_active_provider_name()

        if env_key:
            st.markdown(
                f'<span class="api-status-ok">✅ {provider_name} key loaded from .env</span>',
                unsafe_allow_html=True,
            )
            model_var = "GEMINI_MODEL" if provider_name == "Gemini" else "OPENAI_MODEL"
            model = os.environ.get(model_var, "").strip()
            st.caption(f"Using {model}" if model else "Key is securely stored in your .env file")
        else:
            st.markdown(
                '<span class="api-status-no">⚠️ No AI key — add GEMINI_API_KEY to .env file</span>',
                unsafe_allow_html=True,
            )
            st.caption("Set a Gemini or OpenAI key in the project root .env file")

        st.markdown("---")

        # Navigation
        unlocked = st.session_state.plan_generated
        labels = []
        for i, label in enumerate(SECTION_LABELS):
            if i == 0:
                labels.append(label)
            else:
                labels.append(label if unlocked else f"🔒 {label}")

        selection = st.radio(
            "Navigate",
            labels,
            label_visibility="collapsed",
        )

        idx = labels.index(selection) + 1
        st.caption(f"Step {idx} of 8")

        return selection


# ---------------------------------------------------------------------------
# Generate plan handler
# ---------------------------------------------------------------------------

def on_generate_plan():
    """Eagerly call all services and populate session state."""
    trend = st.session_state.trend
    courses = cached_load_courses()
    teachers = cached_load_teachers()
    api_key = _get_effective_api_key()

    # 1. Match
    match_result = matcher.match_trend_to_course(trend, courses)
    st.session_state.match_result = match_result
    st.session_state.course = match_result["course"]

    # 2. Load material
    material_file = st.session_state.course.get("material_file", "")
    material_text = cached_load_material(material_file)
    st.session_state.material_text = material_text

    # 3. Analyze material
    analysis = material_analyzer.analyze(material_text)
    st.session_state.analysis = analysis

    # 4. AI summary
    summary, used_fallback = ai_service.summarize(material_text, api_key=api_key)
    st.session_state.summary = summary
    st.session_state.summary_used_fallback = used_fallback

    # 5. Find teacher
    teacher_id = st.session_state.course.get("teacher_id", "")
    teacher = None
    for t in teachers:
        if t.get("teacher_id") == teacher_id:
            teacher = t
            break
    if teacher is None and teachers:
        teacher = teachers[0]
    st.session_state.teacher = teacher

    # 6. Generate programme (AI first, deterministic fallback)
    _generate_programme_with_ai(api_key)
    programme = st.session_state.programme

    # 7. Generate personalized content (AI or fallback)
    _regenerate_personalized_learning(api_key)

    # 8. Generate marketing content (AI or fallback)
    mk_data, mk_fallback = ai_service.generate_marketing_content(
        programme.get("title", ""),
        st.session_state.course.get("course_name", ""),
        analysis["weeks"],
        analysis["ects"],
        api_key=api_key,
    )
    if mk_data and not mk_fallback:
        st.session_state.marketing_content = mk_data
        st.session_state.marketing_used_fallback = False
    else:
        st.session_state.marketing_content = marketing.get_marketing_content(programme)
        st.session_state.marketing_used_fallback = True

    st.session_state.brochure_text = None  # Reset brochure
    st.session_state.marketing_image_paths = {}
    st.session_state.marketing_image_status = None
    st.session_state.marketing_image_message = None
    st.session_state.talent_results = None
    st.session_state.talent_search_status = None
    st.session_state.recruitment_emails = {}
    st.session_state.programme_regen_status = None
    st.session_state.programme_regen_message = None
    st.session_state.personalization_regen_status = None
    st.session_state.personalization_regen_message = None
    st.session_state.question_regen_messages = {}
    st.session_state.summary_regen_status = None
    st.session_state.summary_regen_message = None

    # 9. Mark as generated
    st.session_state.plan_generated = True


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_home():
    st.markdown('<div class="section-title">🎓 CoursePilot AI</div>', unsafe_allow_html=True)
    st.markdown("*Turning Xamk courses into trend-based year-round short programmes*")
    st.markdown("---")

    trends = st.session_state.trends
    if not trends:
        st.error("⚠️ Mock data not loaded. Check that data/trends.json exists.")
        return

    # Trend selection
    st.markdown("#### 📈 Trending Topics")
    st.markdown("Select a trend to explore and generate a course plan.")
    st.markdown("")

    # Show trends as selectable cards
    trend_names = [t["trend"] for t in trends]

    # Default selection
    if st.session_state.selected_trend_name is None:
        st.session_state.selected_trend_name = trend_names[0]

    # Render trend cards in columns
    cols = st.columns(len(trends))
    for i, (col, trend) in enumerate(zip(cols, trends)):
        with col:
            is_selected = (trend["trend"] == st.session_state.selected_trend_name)
            card_class = "trend-card-selected" if is_selected else "trend-card"
            badge_class = "badge-trending" if trend["status"] == "Trending" else "badge-rising"

            st.markdown(
                f'<div class="{card_class}">'
                f'<h4 style="margin:0 0 6px;">🔥 {trend["trend"]}</h4>'
                f'<span class="{badge_class}">{trend["status"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.metric("Score", trend["score"], label_visibility="visible")

            if st.button(
                "✅ Selected" if is_selected else "Select",
                key=f"select_trend_{i}",
                type="primary" if is_selected else "secondary",
                width="stretch",
            ):
                st.session_state.selected_trend_name = trend["trend"]
                st.session_state.plan_generated = False  # Reset if changing trend
                st.rerun()

    # Show details of selected trend
    selected_trend = None
    for t in trends:
        if t["trend"] == st.session_state.selected_trend_name:
            selected_trend = t
            break

    if selected_trend:
        st.session_state.trend = selected_trend

        st.markdown("---")
        st.markdown(f"#### 🎯 Selected: {selected_trend['trend']}")
        st.markdown(f"**Reason:** {selected_trend['reason']}")

        chips_html = " ".join(
            f'<span class="chip">{kw}</span>' for kw in selected_trend["keywords"]
        )
        st.markdown(f"**Keywords:** {chips_html}", unsafe_allow_html=True)

        st.markdown("")

        # Button or success banner
        if st.session_state.plan_generated:
            st.markdown(
                '<div class="success-banner">'
                "✅ Plan generated — use the sidebar to explore sections 2–8."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            if st.button("🚀 Generate Course Plan", type="primary", width="stretch"):
                with st.spinner("Generating course plan with AI..."):
                    on_generate_plan()
                st.rerun()


def render_course_match():
    st.markdown('<div class="section-title">📊 Course Match</div>', unsafe_allow_html=True)
    st.markdown("---")

    mr = st.session_state.match_result
    trend = st.session_state.trend
    course = st.session_state.course

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("#### 📈 Selected Trend")
        st.markdown(f"**{trend['trend']}**")
        chips = " ".join(f'<span class="chip">{kw}</span>' for kw in trend["keywords"])
        st.markdown(chips, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("#### 📚 Matched Course")
        st.markdown(f"**{course['course_name']}**")
        st.markdown(f"*{course['description']}*")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    c1, c2 = st.columns([1, 3])
    with c1:
        st.metric("Match Score", f"{mr['score']}%")
    with c2:
        st.markdown(f"**{mr['reason']}**")
        match_chips = " ".join(
            f'<span class="chip">{kw}</span>' for kw in mr["matching_keywords"]
        )
        st.markdown(f"Matching keywords: {match_chips}", unsafe_allow_html=True)


def render_summary():
    st.markdown(
        '<div class="section-title">🤖 AI Summary & Material Analysis</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    material_text = st.session_state.material_text

    if not material_text:
        st.error("⚠️ Course material not found. The file may be missing.")

    with st.expander("📄 Material Preview", expanded=False):
        preview = material_text[:500] if material_text else "(no content)"
        st.code(preview, language=None)

    st.markdown("#### 💡 AI Summary")
    st.markdown(
        f'<div class="info-card">{st.session_state.summary}</div>',
        unsafe_allow_html=True,
    )

    regen_message = st.session_state.summary_regen_message
    if regen_message:
        regen_status = st.session_state.summary_regen_status
        if regen_status == "success":
            st.success(regen_message)
        elif regen_status == "warning":
            st.warning(regen_message)
        else:
            st.error(regen_message)

    api_key = _get_effective_api_key()

    if st.session_state.summary_used_fallback:
        st.caption("⚠️ Using offline fallback summary")
    else:
        st.caption(f"✨ Summary generated by {_get_active_provider_name()}")

    if st.button(
        "🔄 Regenerate with AI",
        key="regen_summary",
        type="primary",
        disabled=not bool(api_key),
        help="Requires GEMINI_API_KEY or OPENAI_API_KEY in the .env file.",
    ):
        with st.spinner("Generating AI summary..."):
            if not st.session_state.material_text:
                st.session_state.summary_regen_status = "error"
                st.session_state.summary_regen_message = (
                    "Course material is missing, so the AI summary cannot be regenerated."
                )
            else:
                summary, used_fallback = ai_service.summarize(
                    st.session_state.material_text, api_key=api_key
                )
                st.session_state.summary = summary
                st.session_state.summary_used_fallback = used_fallback

                if used_fallback:
                    reason = ai_service.get_last_error() or "The AI provider returned no usable summary."
                    st.session_state.summary_regen_status = "error"
                    st.session_state.summary_regen_message = (
                        f"AI regeneration did not complete. {reason}"
                    )
                else:
                    chapters, final_assignment, p_fallback = personalization.get_personalized_chapters(
                        st.session_state.course.get("course_name", ""),
                        "nursing",
                        api_key=api_key,
                    )
                    st.session_state.personalized_chapters = chapters
                    st.session_state.personalized_final_assignment = final_assignment
                    st.session_state.personalization_used_fallback = p_fallback

                    if p_fallback:
                        reason = ai_service.get_last_error() or "Personalized content used fallback."
                        st.session_state.summary_regen_status = "warning"
                        st.session_state.summary_regen_message = (
                            f"AI summary regenerated. Personalized learning stayed offline: {reason}"
                        )
                    else:
                        st.session_state.summary_regen_status = "success"
                        st.session_state.summary_regen_message = (
                            f"AI summary regenerated successfully with {_get_active_provider_name()}."
                        )
        st.rerun()

    if not api_key:
        st.info("Add GEMINI_API_KEY or OPENAI_API_KEY to the .env file, then reload this page to enable regeneration.")

    st.markdown("")
    analysis = st.session_state.analysis
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Material Size", analysis["size"])
    with c2:
        st.metric("Recommended Duration", f"{analysis['weeks']} weeks")
    with c3:
        st.metric("Credits", f"{analysis['ects']} ECTS")

    st.caption(
        "Size rules: Small → 1 week, Medium → 2 weeks, Large → 3 weeks, "
        "Very Large → 4 weeks. Credits always 3 ECTS."
    )


def render_programme():
    st.markdown(
        '<div class="section-title">📋 Generated Programme</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    prog = st.session_state.programme

    st.markdown(
        f'<div class="info-card"><h3>🎮 {prog.get("title", "Generated Programme")}</h3></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.programme_used_fallback:
        st.caption("⚠️ Using offline fallback programme")
    else:
        st.caption(f"✨ Programme generated by {_get_active_provider_name()}")

    if st.session_state.programme_regen_message:
        if st.session_state.programme_regen_status == "success":
            st.success(st.session_state.programme_regen_message)
        else:
            st.error(st.session_state.programme_regen_message)

    api_key = _get_effective_api_key()
    if st.button(
        "🔄 Regenerate Programme with AI",
        key="regen_programme",
        type="primary",
        disabled=not bool(api_key),
        help="Requires GEMINI_API_KEY or OPENAI_API_KEY in the .env file.",
    ):
        with st.spinner("Generating programme plan with AI..."):
            ok = _generate_programme_with_ai(api_key)
            if ok:
                st.session_state.programme_regen_status = "success"
                st.session_state.programme_regen_message = (
                    f"Programme regenerated successfully with {_get_active_provider_name()}."
                )
                st.session_state.marketing_image_paths = {}
                st.session_state.brochure_text = None
            else:
                st.session_state.programme_regen_status = "error"
                st.session_state.programme_regen_message = (
                    ai_service.get_last_error() or "Programme regeneration used the offline fallback."
                )
        st.rerun()

    if not api_key:
        st.info("Add GEMINI_API_KEY or OPENAI_API_KEY to .env to regenerate the programme with AI.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="detail-item"><span class="detail-label">Based on:</span> {prog.get("based_on", "")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-item"><span class="detail-label">ECTS:</span> {prog.get("ects", "")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-item"><span class="detail-label">Duration:</span> {prog.get("duration_weeks", "")} weeks</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-item"><span class="detail-label">Mode:</span> {prog.get("mode", "")}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="detail-item"><span class="detail-label">Teacher:</span> {prog.get("teacher", "")}</div>', unsafe_allow_html=True)
        months_str = ", ".join(prog.get("available_months", []))
        st.markdown(f'<div class="detail-item"><span class="detail-label">Available months:</span> {months_str}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-item"><span class="detail-label">Target students:</span> {prog.get("target_students", "")}</div>', unsafe_allow_html=True)

    st.markdown("")

    outcomes = prog.get("learning_outcomes", [])
    if outcomes:
        with st.expander("🎯 Learning Outcomes", expanded=True):
            for outcome in outcomes:
                st.markdown(f"• {outcome}")

    for week_name, topics in prog.get("weekly_structure", {}).items():
        with st.expander(f"📅 {week_name}", expanded=True):
            for topic in topics:
                st.markdown(f"• {topic}")

    if prog.get("assessment"):
        st.markdown("#### 🧪 Assessment")
        st.markdown(f'<div class="info-card">{prog["assessment"]}</div>', unsafe_allow_html=True)

    if prog.get("demo_pitch"):
        st.info(f"💡 {prog['demo_pitch']}")


def render_personalized_learning():
    st.markdown(
        '<div class="section-title">🎓 Personalized Learning</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown(
        '<div class="nursing-banner">'
        "Viewing as: 🩺 Nursing student interested in IT and electronics"
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption("Admin editing controls are visible in this demo; student-side editing is intentionally not modeled here.")

    api_key = _get_effective_api_key()

    # Show AI status and regenerate option
    if st.session_state.personalization_used_fallback:
        st.caption("⚠️ Using offline fallback content")
    else:
        st.caption(f"✨ Content personalized by {_get_active_provider_name()} in real time")

    if st.session_state.personalization_regen_message:
        if st.session_state.personalization_regen_status == "success":
            st.success(st.session_state.personalization_regen_message)
        else:
            st.error(st.session_state.personalization_regen_message)

    if st.button(
        "🔄 Regenerate Personalized Learning with AI",
        key="regen_personalization",
        type="primary",
        disabled=not bool(api_key),
        help="Requires GEMINI_API_KEY or OPENAI_API_KEY in the .env file.",
    ):
        with st.spinner("Generating personalized content and mini-games with AI..."):
            ok = _regenerate_personalized_learning(api_key)
            if ok:
                st.session_state.personalization_regen_status = "success"
                st.session_state.personalization_regen_message = (
                    f"Personalized chapters and mini-games regenerated with {_get_active_provider_name()}."
                )
            else:
                st.session_state.personalization_regen_status = "error"
                st.session_state.personalization_regen_message = (
                    ai_service.get_last_error() or "Personalized learning regeneration used fallback content."
                )
        st.rerun()

    if not api_key:
        st.info("Add GEMINI_API_KEY or OPENAI_API_KEY to .env to regenerate personalized learning with AI.")

    chapters = list(st.session_state.personalized_chapters or [])

    for idx, ch in enumerate(chapters):
        sync_editor = st.session_state.pending_question_sync == idx
        ch = _repair_blank_chapter_copy(idx, ch)
        _prime_chapter_editor_state(idx, ch, force=sync_editor)
        if sync_editor:
            st.session_state.pending_question_sync = None
        game = ch.get("minigame", {}) or {}

        with st.expander(f"Admin edit: {ch.get('title', f'Chapter {idx + 1}')}", expanded=False):
            title_input = st.text_input("Chapter title", key=f"ch_title_{idx}")
            standard_input = st.text_area(
                "Standard explanation",
                key=f"ch_standard_{idx}",
                height=110,
            )
            personalized_input = st.text_area(
                "Personalized explanation shown to student",
                key=f"ch_personalized_{idx}",
                height=110,
            )
            ch["title"] = _keep_existing_when_blank(ch.get("title"), title_input)
            ch["standard_explanation"] = _keep_existing_when_blank(
                ch.get("standard_explanation"),
                standard_input,
            )
            ch["personalized_explanation"] = _keep_existing_when_blank(
                ch.get("personalized_explanation"),
                personalized_input,
            )

            st.markdown("**Mini-game question editor**")
            game_name_input = st.text_input("Mini-game name", key=f"game_name_admin_{idx}")
            game_description_input = st.text_area(
                "Mini-game description",
                key=f"game_description_admin_{idx}",
                height=90,
            )
            game_scenario_input = st.text_area(
                "Question / scenario shown to student",
                key=f"game_scenario_admin_{idx}",
                height=100,
            )
            game["name"] = _keep_existing_when_blank(game.get("name"), game_name_input)
            game["description"] = _keep_existing_when_blank(game.get("description"), game_description_input)
            game["scenario"] = _keep_existing_when_blank(game.get("scenario"), game_scenario_input)
            choices_text = st.text_area(
                "Answer choices, one per line",
                key=f"game_choices_text_{idx}",
                height=120,
            )
            choices = [line.strip() for line in choices_text.splitlines() if line.strip()]
            if not choices:
                choices = game.get("choices", []) or ["Option A", "Option B"]
            game["choices"] = choices

            current_correct = (
                game.get("correct_choice")
                or st.session_state.get(f"game_correct_choice_editor_{idx}")
                or st.session_state.get(f"game_correct_choice_{idx}")
            )
            if current_correct not in choices:
                current_correct = choices[0]
            game["correct_choice"] = st.selectbox(
                "Correct answer",
                choices,
                index=choices.index(current_correct),
                key=f"game_correct_choice_editor_{idx}",
            )
            feedback_input = st.text_area(
                "Feedback after correct answer",
                key=f"game_feedback_admin_{idx}",
                height=90,
            )
            game["feedback"] = _keep_existing_when_blank(game.get("feedback"), feedback_input)

            if st.button(
                "🔄 Regenerate question again",
                key=f"regen_question_{idx}",
                disabled=not bool(api_key),
                help="Regenerates only this mini-game question with AI.",
            ):
                with st.spinner("Regenerating this question with AI..."):
                    _regenerate_single_question(idx, api_key)
                st.rerun()

            message = (st.session_state.question_regen_messages or {}).get(idx)
            if message:
                if message.get("status") == "success":
                    st.success(message.get("text", "Question regenerated."))
                else:
                    st.error(message.get("text", "Question regeneration failed."))

        ch["minigame"] = game
        chapters[idx] = ch
        st.session_state.personalized_chapters = chapters

        st.markdown(
            f'<div class="chapter-card">'
            f'<h4>{ch["title"]}</h4>'
            f'<div class="chapter-label">Standard Explanation</div>'
            f'<p>{ch["standard_explanation"]}</p>'
            f'<div class="chapter-label">Personalized for Nursing</div>'
            f'<p>{ch["personalized_explanation"]}</p>'
            f'<div class="minigame-card">'
            f'<div class="mg-name">🎮 {game.get("name", "Mini-game")}</div>'
            f'<p>{game.get("description", "")}</p>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        scenario = game.get("scenario", "")
        choices = game.get("choices", [])
        correct_choice = game.get("correct_choice", "")
        feedback = game.get("feedback", "")
        if scenario and len(choices) >= 2:
            if correct_choice not in choices:
                correct_choice = choices[0]
            if st.session_state.get(f"game_choice_{idx}") not in choices:
                st.session_state[f"game_choice_{idx}"] = choices[0]
            st.markdown(
                f'<div class="play-card"><strong>Play:</strong> {scenario}</div>',
                unsafe_allow_html=True,
            )
            selected = st.radio(
                "Choose an action",
                choices,
                key=f"game_choice_{idx}",
                label_visibility="collapsed",
            )
            if st.button("Check answer", key=f"check_game_{idx}"):
                if selected == correct_choice:
                    st.success(feedback or "Correct.")
                else:
                    st.warning(f"Try again. A stronger choice is: {correct_choice}")

        if st.button(
            "🔄 Regenerate question again",
            key=f"regen_question_visible_{idx}",
            disabled=not bool(api_key),
            help="Regenerates this student-facing question in real time with AI.",
        ):
            with st.spinner("Regenerating this question with AI..."):
                _regenerate_single_question(idx, api_key)
            st.rerun()

    # Final assignment
    st.markdown("---")
    st.markdown("#### 📝 Final Assignment")
    if "final_assignment_editor" not in st.session_state:
        st.session_state["final_assignment_editor"] = st.session_state.personalized_final_assignment
    final_text = st.text_area(
        "Admin edit: final assignment shown to student",
        key="final_assignment_editor",
        height=180,
    )
    st.session_state.personalized_final_assignment = final_text
    st.markdown(
        f'<div class="info-card">{final_text.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )


def render_teacher():
    st.markdown(
        '<div class="section-title">👩‍🏫 Teacher Availability & Recruitment</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    available_tab, recruitment_tab = st.tabs(
        ["Available Teachers", "Recruitment Talent Pool"]
    )

    with available_tab:
        teachers = cached_load_teachers()
        recommended_id = (st.session_state.teacher or {}).get("teacher_id")
        st.markdown("#### Available Teachers From Mock Data")
        for teacher in teachers:
            is_recommended = teacher.get("teacher_id") == recommended_id
            st.markdown(
                f'<div class="info-card"><h3>{teacher["name"]}{" — recommended" if is_recommended else ""}</h3></div>',
                unsafe_allow_html=True,
            )
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown("**Skills**")
                chips = " ".join(f'<span class="chip">{s}</span>' for s in teacher["skills"])
                st.markdown(chips, unsafe_allow_html=True)
            with col2:
                st.markdown("**Available Months**")
                month_chips = " ".join(
                    f'<span class="chip">{m}</span>' for m in teacher["available_months"]
                )
                st.markdown(month_chips, unsafe_allow_html=True)
                st.markdown("**Modes**")
                mode_chips = " ".join(
                    f'<span class="chip">{m}</span>' for m in teacher["available_modes"]
                )
                st.markdown(mode_chips, unsafe_allow_html=True)
            with col3:
                st.metric("Rate", f"€{teacher['hourly_rate']}/h")

        st.info("🗓️ **Recommended season:** Winter / November")

    with recruitment_tab:
        st.markdown("#### Most Probable Teachers From Recruitment Talent Pools")
        st.caption(
            "LinkedIn Talent Solutions/RSC is partner-gated. This demo ranks Xamk's recruitment pool now and can call an approved LinkedIn endpoint when credentials are configured."
        )

        if st.button("🔎 Search Talent Pool + LinkedIn", key="search_talent_pool", type="primary"):
            with st.spinner("Searching recruitment talent pools..."):
                _search_teacher_talents()
            st.rerun()

        if st.session_state.talent_results is None:
            _search_teacher_talents()

        if st.session_state.talent_search_status:
            st.info(st.session_state.talent_search_status)

        emails = st.session_state.recruitment_emails or {}
        for idx, candidate in enumerate(st.session_state.talent_results or []):
            candidate_id = candidate.get("talent_id", candidate.get("name", str(idx)))
            header_col, action_col = st.columns([5, 1])
            with header_col:
                st.markdown(
                    f'<div class="info-card"><h3>{candidate.get("name", "")}</h3>'
                    f'<div class="ai-note">{candidate.get("headline", "")} • {candidate.get("location", "")}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with action_col:
                if st.button("✉️ Email", key=f"email_candidate_{candidate_id}", help="Generate recruitment email"):
                    with st.spinner("Generating recruitment email with AI..."):
                        _generate_recruitment_email(candidate)
                    st.rerun()

            c1, c2 = st.columns([1, 4])
            with c1:
                st.metric("Match", f"{candidate.get('match_score', 0)}%")
            with c2:
                skills = " ".join(
                    f'<span class="chip">{skill}</span>' for skill in candidate.get("skills", [])[:7]
                )
                st.markdown(skills, unsafe_allow_html=True)
                st.markdown(f"**Source:** {candidate.get('source', 'Recruitment pool')}")
                st.markdown(f"**Why likely:** {'; '.join(candidate.get('match_reasons', []))}")
                st.markdown(f"**Notes:** {candidate.get('notes', '')}")
                if candidate.get("linkedin_profile"):
                    st.markdown(f"[LinkedIn profile]({candidate['linkedin_profile']})")

            if candidate_id in emails:
                email_data = emails[candidate_id]
                label = "AI-generated recruitment email"
                if email_data.get("used_fallback"):
                    label += " (fallback)"
                with st.expander(f"✉️ {label}", expanded=True):
                    st.text_area(
                        "Email draft",
                        email_data["text"],
                        height=280,
                        key=f"email_text_{candidate_id}",
                    )

            st.markdown("---")


def render_marketing():
    st.markdown(
        '<div class="section-title">📣 Marketing Generator</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    api_key = _get_effective_api_key()

    # Show AI status
    if st.session_state.marketing_used_fallback:
        st.caption("⚠️ Using offline fallback marketing content")
    else:
        st.caption(f"✨ Marketing content generated by {_get_active_provider_name()}")

    if st.button(
        "🔄 Regenerate Marketing Copy with AI",
        key="regen_marketing",
        type="primary",
        disabled=not bool(api_key),
        help="Requires GEMINI_API_KEY or OPENAI_API_KEY in the .env file.",
    ):
        with st.spinner("Generating marketing content with AI..."):
            prog = st.session_state.programme
            mk_data, mk_fallback = ai_service.generate_marketing_content(
                prog.get("title", ""),
                st.session_state.course.get("course_name", ""),
                st.session_state.analysis["weeks"],
                st.session_state.analysis["ects"],
                api_key=api_key,
            )
            if mk_data and not mk_fallback:
                st.session_state.marketing_content = mk_data
                st.session_state.marketing_used_fallback = False
                st.session_state.marketing_image_paths = {}
            else:
                st.session_state.marketing_content = marketing.get_marketing_content(prog)
                st.session_state.marketing_used_fallback = True
                st.error(ai_service.get_last_error() or "Marketing copy regeneration used fallback content.")
        st.rerun()

    content = st.session_state.marketing_content

    with st.expander("🌐 Website Description", expanded=True):
        st.markdown(content["website"])

    with st.expander("📱 Social Media Post", expanded=False):
        st.markdown(content["social"])

    with st.expander("✉️ Partner School Email", expanded=False):
        st.code(content["email"], language=None)

    with st.expander("💬 Tagline", expanded=False):
        st.markdown(f"**{content['tagline']}**")

    with st.expander("🏆 Selling Points", expanded=False):
        for i, point in enumerate(content["selling_points"], 1):
            st.markdown(f"**{i}.** {point}")

    st.markdown("---")
    st.markdown("#### 🖼️ AI Visual Assets")
    if st.session_state.marketing_image_message:
        if st.session_state.marketing_image_status == "success":
            st.success(st.session_state.marketing_image_message)
        elif st.session_state.marketing_image_status == "warning":
            st.warning(st.session_state.marketing_image_message)
        else:
            st.error(st.session_state.marketing_image_message)

    image_paths = st.session_state.marketing_image_paths or {}
    social_col, brochure_col = st.columns(2)
    with social_col:
        st.markdown("**Social Media Image**")
        if image_paths.get("social"):
            st.image(image_paths["social"], width="stretch")
        if st.button(
            "🎨 Generate Social Image",
            key="generate_social_image",
            disabled=not bool(api_key),
            width="stretch",
        ):
            with st.spinner("Generating social media image..."):
                _generate_marketing_visual("social")
            st.rerun()

    with brochure_col:
        st.markdown("**Brochure / Pamphlet Cover**")
        if image_paths.get("brochure"):
            st.image(image_paths["brochure"], width="stretch")
        if st.button(
            "🎨 Generate Brochure Image",
            key="generate_brochure_image",
            disabled=not bool(api_key),
            width="stretch",
        ):
            with st.spinner("Generating brochure image..."):
                _generate_marketing_visual("brochure")
            st.rerun()

    if not api_key:
        st.info("Add GEMINI_API_KEY or OPENAI_API_KEY to .env to generate marketing images.")

    # Brochure & Pamphlet section
    st.markdown("---")
    with st.expander("📄 Brochure & Pamphlets", expanded=False):
        st.markdown("Generate a professional brochure or pamphlet for the programme using AI.")

        if st.session_state.brochure_text:
            st.markdown(st.session_state.brochure_text)
            st.markdown("---")
            if st.button("🔄 Regenerate Brochure", key="regen_brochure"):
                with st.spinner("Generating new brochure with AI..."):
                    prog = st.session_state.programme
                    brochure, b_fallback = ai_service.generate_brochure(
                        prog.get("title", ""),
                        st.session_state.course.get("course_name", ""),
                        st.session_state.analysis["weeks"],
                        st.session_state.analysis["ects"],
                        prog.get("weekly_structure", {}),
                        api_key=_get_effective_api_key(),
                    )
                    if brochure and not b_fallback:
                        st.session_state.brochure_text = brochure
                        _generate_marketing_visual("brochure")
                    else:
                        st.error(ai_service.get_last_error() or "⚠️ Could not generate brochure. Check your API key and billing.")
                st.rerun()
        else:
            if api_key:
                if st.button("🎨 Generate Brochure & Pamphlet", key="gen_brochure", type="primary", width="stretch"):
                    with st.spinner("Generating brochure with AI..."):
                        prog = st.session_state.programme
                        brochure, b_fallback = ai_service.generate_brochure(
                            prog.get("title", ""),
                            st.session_state.course.get("course_name", ""),
                            st.session_state.analysis["weeks"],
                            st.session_state.analysis["ects"],
                            prog.get("weekly_structure", {}),
                            api_key=api_key,
                        )
                        if brochure and not b_fallback:
                            st.session_state.brochure_text = brochure
                            _generate_marketing_visual("brochure")
                        else:
                            st.error(ai_service.get_last_error() or "⚠️ Could not generate brochure. Check your API key and billing.")
                    st.rerun()
            else:
                st.info("🔑 Add GEMINI_API_KEY or OPENAI_API_KEY to .env to generate brochures.")


def render_income():
    st.markdown(
        '<div class="section-title">💰 Income Estimator</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    students = 25
    price = 450
    costs = 4250

    result = finance.compute(students, price, costs)

    st.markdown("#### 📊 Inputs")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Expected Students", students)
    with c2:
        st.metric("Price per Student", f"€{price}")
    with c3:
        st.metric("Estimated Total Costs", f"€{costs:,}")

    st.markdown("---")

    st.markdown("#### 📈 Results")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Revenue", f"€{result['revenue']:,}")
    with r2:
        st.metric("Profit", f"€{result['profit']:,}")
    with r3:
        st.metric("Break-even Price", f"€{result['break_even_price']:.0f}")
    with r4:
        st.metric("Break-even Students", f"~{result['break_even_students']}")


# ---------------------------------------------------------------------------
# Locked section message
# ---------------------------------------------------------------------------

def render_locked():
    st.markdown(
        '<div class="locked-msg">'
        "🔒 Click <strong>'Generate Course Plan'</strong> on Home to unlock this section."
        "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    inject_css()
    init_state()

    # Load data on first run
    if not st.session_state.data_loaded:
        trends = cached_load_trends()
        courses = cached_load_courses()
        teachers = cached_load_teachers()

        if not trends or not courses:
            st.session_state.data_error = True
        else:
            st.session_state.trends = trends
            st.session_state.trend = trends[0]
            st.session_state.data_loaded = True

    # Sidebar navigation
    selection = render_sidebar()

    # Route to section
    unlocked = st.session_state.plan_generated

    if selection == "1. Home":
        if st.session_state.data_error:
            st.error("⚠️ Mock data not loaded. Check that data/ JSON files exist and are valid.")
        else:
            render_home()

    elif "2. Course Match" in selection:
        render_course_match() if unlocked else render_locked()

    elif "3. AI Summary" in selection:
        render_summary() if unlocked else render_locked()

    elif "4. Programme" in selection:
        render_programme() if unlocked else render_locked()

    elif "5. Personalized Learning" in selection:
        render_personalized_learning() if unlocked else render_locked()

    elif "6. Teacher" in selection:
        render_teacher() if unlocked else render_locked()

    elif "7. Marketing" in selection:
        render_marketing() if unlocked else render_locked()

    elif "8. Income" in selection:
        render_income() if unlocked else render_locked()


if __name__ == "__main__":
    main()
