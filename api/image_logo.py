"""Xamk logo drawing for generated assets."""

from api.image_fonts import load_font


def draw_xamk_logo(draw, x: int, y: int, scale: int = 1) -> None:
    logo_font = load_font(34 * scale, bold=True)
    sub_font = load_font(12 * scale, bold=False)
    draw.rounded_rectangle((x, y, x + 168 * scale, y + 58 * scale), radius=12 * scale, fill="#ffffff")
    draw.rectangle((x + 14 * scale, y + 13 * scale, x + 30 * scale, y + 45 * scale), fill="#00a651")
    draw.text((x + 40 * scale, y + 7 * scale), "Xamk", font=logo_font, fill="#003b5c")
    draw.text((x + 41 * scale, y + 42 * scale), "South-Eastern Finland UAS", font=sub_font, fill="#64748b")
