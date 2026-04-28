"""
data_loader.py — Load mock JSON data and course material text files.

Only module that does file I/O besides AI HTTP calls.
"""

from pathlib import Path

from services.data_file_reader import read_json_list, read_material_text

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
    return read_material_text(_BASE_DIR / "materials" / filename)


def load_json_list(filename: str) -> list:
    path = _BASE_DIR / "data" / filename
    return read_json_list(path, filename)
