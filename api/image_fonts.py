"""Font loading for generated image branding."""

from pathlib import Path


def load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    font_path = next((candidate for candidate in font_candidates(bold) if Path(candidate).exists()), None)
    return ImageFont.truetype(font_path, size=size) if font_path else ImageFont.load_default()


def font_candidates(bold: bool) -> list[str]:
    return [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
