"""Programme payload serializers."""

from typing import Any


def camel_programme(programme: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": programme.get("title", ""),
        "basedOn": programme.get("based_on", programme.get("basedOn", "")),
        "ects": programme.get("ects", 3),
        "durationWeeks": programme.get("duration_weeks", programme.get("durationWeeks", 0)),
        "mode": programme.get("mode", ""),
        "teacher": programme.get("teacher", ""),
        "teacherId": programme.get("teacher_id", programme.get("teacherId", "")),
        "availableMonths": programme.get("available_months", programme.get("availableMonths", [])),
        "targetStudents": programme.get("target_students", programme.get("targetStudents", "")),
        "outcomes": programme.get("learning_outcomes", programme.get("outcomes", [])),
        "weeklyStructure": programme.get("weekly_structure", programme.get("weeklyStructure", {})),
        "assessment": programme.get("assessment", ""),
        "demoPitch": programme.get("demo_pitch", programme.get("demoPitch", "")),
    }


def snake_programme(programme: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": programme.get("title", ""),
        "based_on": programme.get("based_on", programme.get("basedOn", "")),
        "ects": programme.get("ects", 3),
        "duration_weeks": programme.get("duration_weeks", programme.get("durationWeeks", 0)),
        "mode": programme.get("mode", ""),
        "teacher": programme.get("teacher", ""),
        "teacher_id": programme.get("teacher_id", programme.get("teacherId", "")),
        "available_months": programme.get("available_months", programme.get("availableMonths", [])),
        "target_students": programme.get("target_students", programme.get("targetStudents", "")),
        "learning_outcomes": programme.get("learning_outcomes", programme.get("outcomes", [])),
        "weekly_structure": programme.get("weekly_structure", programme.get("weeklyStructure", {})),
        "assessment": programme.get("assessment", ""),
        "demo_pitch": programme.get("demo_pitch", programme.get("demoPitch", "")),
    }
