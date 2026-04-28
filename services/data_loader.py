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
    path = _BASE_DIR / "data" / "trends.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("trends.json not found at %s", path)
        return []
    except json.JSONDecodeError:
        logger.warning("trends.json is corrupt at %s", path)
        return []


def load_courses() -> list:
    """Load courses from data/courses.json. Returns [] on failure."""
    path = _BASE_DIR / "data" / "courses.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("courses.json not found at %s", path)
        return []
    except json.JSONDecodeError:
        logger.warning("courses.json is corrupt at %s", path)
        return []


def load_teachers() -> list:
    """Load teachers from data/teachers.json. Returns [] on failure."""
    path = _BASE_DIR / "data" / "teachers.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("teachers.json not found at %s", path)
        return []
    except json.JSONDecodeError:
        logger.warning("teachers.json is corrupt at %s", path)
        return []


def load_material(filename: str) -> str:
    """Load a course material text file from materials/. Returns '' on failure."""
    path = _BASE_DIR / "materials" / filename
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("Material file not found: %s", path)
        return ""
    except Exception as e:
        logger.warning("Error reading material file %s: %s", path, e)
        return ""
