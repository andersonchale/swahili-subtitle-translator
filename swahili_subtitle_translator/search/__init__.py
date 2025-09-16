"""Subtitle search and download integration."""

from .engine import SubtitleSearchEngine, search_subtitles
from .sources import (
    SubtitleSource,
    SubtitleSourceError,
    OpenSubtitlesSource,
    SubsceneSource, 
    YIFYSubtitlesSource
)
from .models import (
    SearchResult, 
    SearchQuery,
    SourceType,
    SubtitleFormat,
    SubtitleMetadata
)

__all__ = [
    "SubtitleSearchEngine",
    "search_subtitles",
    "SubtitleSource",
    "SubtitleSourceError",
    "OpenSubtitlesSource", 
    "SubsceneSource",
    "YIFYSubtitlesSource",
    "SearchResult",
    "SearchQuery",
    "SourceType",
    "SubtitleFormat",
    "SubtitleMetadata"
]
