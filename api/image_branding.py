"""Apply Xamk branding overlays to generated images."""

from io import BytesIO

from api.image_footer import footer_box
from api.image_logo import draw_xamk_logo


def apply_xamk_branding(image_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    try:
        return branded_png(image_bytes)
    except Exception:
        return (image_bytes, mime_type or "image/png")


def branded_png(image_bytes: bytes) -> tuple[bytes, str]:
    from PIL import Image, ImageDraw

    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)
    margin = max(28, image.width // 24)
    draw_xamk_logo(draw, margin, margin, scale=max(1, round(image.width / 1000)))
    footer_box(draw, image, margin)
    return (png_bytes(image), "image/png")


def png_bytes(image) -> bytes:
    output = BytesIO()
    image.save(output, "PNG")
    return output.getvalue()
