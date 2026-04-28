"""Compatibility facade for API payload serializers."""

from api.analysis_serializers import camel_analysis, snake_analysis
from api.chapter_serializers import camel_chapter, camel_personalized, snake_chapter
from api.marketing_serializers import camel_marketing, snake_marketing
from api.programme_serializers import camel_programme, snake_programme
from api.summary_serializers import summary_card
from api.talent_serializers import camel_talent

__all__ = [
    "camel_analysis",
    "camel_chapter",
    "camel_marketing",
    "camel_personalized",
    "camel_programme",
    "camel_talent",
    "snake_analysis",
    "snake_chapter",
    "snake_marketing",
    "snake_programme",
    "summary_card",
]
