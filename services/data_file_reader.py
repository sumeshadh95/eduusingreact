"""Small file-reading helpers for demo data sources."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def read_material_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Material file not found: %s", path)
    except Exception as exc:
        logger.warning("Error reading material file %s: %s", path, exc)
    return ""


def read_json_list(path: Path, filename: str) -> list:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning("%s not found at %s", filename, path)
    except json.JSONDecodeError:
        logger.warning("%s is corrupt at %s", filename, path)
    return []
