"""
Data models for subtitle search and metadata.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class SubtitleFormat(Enum):
    """Supported subtitle formats."""
    SRT = "srt"
    ASS = "ass"
    SSA = "ssa"
    VTT = "vtt"
    SUB = "sub"


class SourceType(Enum):
    """Subtitle source types."""
    OPENSUBTITLES = "opensubtitles"
    SUBSCENE = "subscene" 
    YIFY = "yify"
    MOCK = "mock"
    LOCAL = "local"


@dataclass
class SubtitleMetadata:
    """Metadata for a subtitle file."""
    
    title: str
    year: Optional[int] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    language: str = "en"
    format: SubtitleFormat = SubtitleFormat.SRT
    release_info: Optional[str] = None
    fps: Optional[float] = None
    hearing_impaired: bool = False
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        if isinstance(self.format, str):
            self.format = SubtitleFormat(self.format.lower())


@dataclass
class SearchResult:
    """Result from subtitle search."""
    
    id: str
    title: str
    year: Optional[int]
    language: str
    format: SubtitleFormat
    source: SourceType
    download_url: str
    release_info: Optional[str] = None
    uploader: Optional[str] = None
    download_count: Optional[int] = None
    rating: Optional[float] = None
    hearing_impaired: bool = False
    fps: Optional[float] = None
    file_size: Optional[int] = None
    upload_date: Optional[datetime] = None
    
    # Additional metadata
    season: Optional[int] = None
    episode: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        if isinstance(self.format, str):
            self.format = SubtitleFormat(self.format.lower())
        if isinstance(self.source, str):
            self.source = SourceType(self.source.lower())
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_tv_show(self) -> bool:
        """Check if this is a TV show subtitle."""
        return self.season is not None or self.episode is not None
    
    @property
    def display_name(self) -> str:
        """Get display-friendly name."""
        name = self.title
        if self.year:
            name += f" ({self.year})"
        if self.season is not None:
            name += f" S{self.season:02d}"
        if self.episode is not None:
            name += f"E{self.episode:02d}"
        if self.release_info:
            name += f" [{self.release_info}]"
        return name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "language": self.language,
            "format": self.format.value,
            "source": self.source.value,
            "download_url": self.download_url,
            "release_info": self.release_info,
            "uploader": self.uploader,
            "download_count": self.download_count,
            "rating": self.rating,
            "hearing_impaired": self.hearing_impaired,
            "fps": self.fps,
            "file_size": self.file_size,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "season": self.season,
            "episode": self.episode,
            "display_name": self.display_name,
            "metadata": self.metadata
        }


@dataclass
class SearchQuery:
    """Search query parameters."""
    
    title: str
    year: Optional[int] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    language: str = "en"
    hearing_impaired: Optional[bool] = None
    release_info: Optional[str] = None
    
    # Search options
    limit: int = 10
    sources: Optional[List[SourceType]] = None
    
    def __post_init__(self):
        """Validate and normalize search parameters."""
        if self.sources is None:
            self.sources = list(SourceType)
        elif isinstance(self.sources, list) and self.sources:
            # Convert string sources to enum
            normalized_sources = []
            for source in self.sources:
                if isinstance(source, str):
                    try:
                        normalized_sources.append(SourceType(source.lower()))
                    except ValueError:
                        continue  # Skip invalid sources
                elif isinstance(source, SourceType):
                    normalized_sources.append(source)
            self.sources = normalized_sources
    
    @property
    def is_tv_show(self) -> bool:
        """Check if this is a TV show query."""
        return self.season is not None or self.episode is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "year": self.year,
            "season": self.season,
            "episode": self.episode,
            "language": self.language,
            "hearing_impaired": self.hearing_impaired,
            "release_info": self.release_info,
            "limit": self.limit,
            "sources": [s.value for s in self.sources] if self.sources else []
        }
