"""Analysis payload serializers."""

from typing import Any


def camel_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "size": analysis.get("size", ""),
        "weeks": analysis.get("weeks", 0),
        "ects": analysis.get("ects", 3),
        "wordCount": analysis.get("word_count", analysis.get("wordCount", 0)),
    }


def snake_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "size": analysis.get("size", ""),
        "weeks": analysis.get("weeks", 0),
        "ects": analysis.get("ects", 3),
        "word_count": analysis.get("word_count", analysis.get("wordCount", 0)),
    }
