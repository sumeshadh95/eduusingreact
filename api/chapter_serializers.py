"""Personalized-learning chapter serializers."""

from typing import Any


def camel_chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    game = chapter_game(chapter)
    return {
        "title": chapter.get("title", ""),
        "standard": chapter.get("standard_explanation", chapter.get("standard", "")),
        "personalized": chapter.get("personalized_explanation", chapter.get("personalized", "")),
        "game": {
            "name": game.get("name", ""),
            "description": game.get("description", ""),
            "scenario": game.get("scenario", ""),
            "choices": game.get("choices", []),
            "correctChoice": game.get("correct_choice", game.get("correctChoice", "")),
            "feedback": game.get("feedback", ""),
        },
    }


def snake_chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    game = chapter_game(chapter)
    return {
        "title": chapter.get("title", ""),
        "standard_explanation": chapter.get("standard_explanation", chapter.get("standard", "")),
        "personalized_explanation": chapter.get("personalized_explanation", chapter.get("personalized", "")),
        "minigame": {
            "name": game.get("name", ""),
            "description": game.get("description", ""),
            "scenario": game.get("scenario", ""),
            "choices": game.get("choices", []),
            "correct_choice": game.get("correct_choice", game.get("correctChoice", "")),
            "feedback": game.get("feedback", ""),
        },
    }


def camel_personalized(
    chapters: list[dict[str, Any]], final_assignment: str, used_fallback: bool
) -> dict[str, Any]:
    return {
        "studentProfile": "Nursing student interested in IT and electronics",
        "chapters": [camel_chapter(chapter) for chapter in chapters],
        "finalAssignment": final_assignment,
        "usedFallback": used_fallback,
    }


def chapter_game(chapter: dict[str, Any]) -> dict[str, Any]:
    return chapter.get("minigame", chapter.get("game", {})) or {}
