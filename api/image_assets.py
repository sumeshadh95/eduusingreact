"""Generated marketing-image branding and storage."""

import time
from io import BytesIO
from pathlib import Path

from api.config import ASSET_DIR


def load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def draw_xamk_logo(draw, x: int, y: int, scale: int = 1) -> None:
    logo_font = load_font(34 * scale, bold=True)
    sub_font = load_font(12 * scale, bold=False)
    draw.rounded_rectangle((x, y, x + 168 * scale, y + 58 * scale), radius=12 * scale, fill="#ffffff")
    draw.rectangle((x + 14 * scale, y + 13 * scale, x + 30 * scale, y + 45 * scale), fill="#00a651")
    draw.text((x + 40 * scale, y + 7 * scale), "Xamk", font=logo_font, fill="#003b5c")
    draw.text((x + 41 * scale, y + 42 * scale), "South-Eastern Finland UAS", font=sub_font, fill="#64748b")


def footer_box(draw, image, margin: int) -> None:
    footer_font = load_font(max(18, image.width // 46), bold=True)
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


def apply_xamk_branding(image_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    try:
        from PIL import Image, ImageDraw

        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(image)
        scale = max(1, round(image.width / 1000))
        margin = max(28, image.width // 24)
        draw_xamk_logo(draw, margin, margin, scale=scale)
        footer_box(draw, image, margin)

        output = BytesIO()
        image.save(output, "PNG")
        return (output.getvalue(), "image/png")
    except Exception:
        return (image_bytes, mime_type or "image/png")


def save_generated_image(image_bytes: bytes, mime_type: str, prefix: str) -> str:
    ASSET_DIR.mkdir(exist_ok=True)
    branded_bytes, branded_mime = apply_xamk_branding(image_bytes, mime_type)
    ext = ".jpg" if "jpeg" in (branded_mime or "").lower() else ".png"
    path = ASSET_DIR / f"{prefix}_{int(time.time())}{ext}"
    path.write_bytes(branded_bytes)
    return f"/generated_assets/{path.name}"
