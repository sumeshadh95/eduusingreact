"""
data_loader.py — Load mock JSON data and course material text files.

Only module that does file I/O besides AI HTTP calls.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).parent.parent


def load_trends() -> list:
    """Load trends from data/trends.json. Returns [] on failure."""
    return load_json_list("trends.json")


def load_courses() -> list:
    """Load courses from data/courses.json. Returns [] on failure."""
    return load_json_list("courses.json")


def load_teachers() -> list:
    """Load teachers from data/teachers.json. Returns [] on failure."""
    return load_json_list("teachers.json")


def load_material(filename: str) -> str:
    """Load a course material text file from materials/. Returns '' on failure."""
    path = _BASE_DIR / "materials" / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Material file not found: %s", path)
        return ""
    except Exception as e:
        logger.warning("Error reading material file %s: %s", path, e)
        return ""


def load_json_list(filename: str) -> list:
    path = _BASE_DIR / "data" / filename
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning("%s not found at %s", filename, path)
    except json.JSONDecodeError:
        logger.warning("%s is corrupt at %s", filename, path)
    return []
