"""Store generated marketing images."""

import time

from api.config import ASSET_DIR
from api.image_branding import apply_xamk_branding


def save_generated_image(image_bytes: bytes, mime_type: str, prefix: str) -> str:
    ASSET_DIR.mkdir(exist_ok=True)
    branded_bytes, branded_mime = apply_xamk_branding(image_bytes, mime_type)
    path = ASSET_DIR / f"{prefix}_{int(time.time())}{image_extension(branded_mime)}"
    path.write_bytes(branded_bytes)
    return f"/generated_assets/{path.name}"


def image_extension(mime_type: str) -> str:
    return ".jpg" if "jpeg" in (mime_type or "").lower() else ".png"
