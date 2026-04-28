"""Footer drawing for generated assets."""

from api.image_fonts import load_font


def footer_box(draw, image, margin: int) -> None:
    footer_font = load_font(max(18, image.width // 46), bold=True)
    metrics = footer_metrics(draw, image, margin, footer_font)
    draw.rounded_rectangle(
        metrics["box"],
        radius=max(12, image.width // 90),
        fill="#003b5c",
    )
    draw.text(metrics["text_position"], metrics["text"], font=footer_font, fill="#ffffff")


def footer_metrics(draw, image, margin: int, footer_font) -> dict:
    footer_text = "Xamk Continuing Education"
    footer_width = text_width(draw, footer_text, footer_font)
    pad_x = max(18, image.width // 70)
    pad_y = max(10, image.width // 110)
    x2 = image.width - margin
    y2 = image.height - margin
    return {
        "text": footer_text,
        "box": (x2 - footer_width - (pad_x * 2), y2 - footer_font.size - (pad_y * 2), x2, y2),
        "text_position": (x2 - footer_width - pad_x, y2 - footer_font.size - pad_y - 2),
    }


def text_width(draw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]
