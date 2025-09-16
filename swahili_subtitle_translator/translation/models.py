"""
Data models for translation functionality.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from datetime import datetime
import uuid


class TranslationService(Enum):
    """Supported translation services."""
    GOOGLE_TRANSLATE = "google_translate"
    OPENAI_GPT = "openai_gpt"
    AZURE_TRANSLATOR = "azure_translator"
    OFFLINE_MODEL = "offline_model"
    MOCK = "mock"  # For testing


class LanguageCode(Enum):
    """Supported language codes (ISO 639-1)."""
    ENGLISH = "en"
    SWAHILI = "sw"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ARABIC = "ar"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    HINDI = "hi"


@dataclass
class TranslationRequest:
    """Request for translation of text content."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    source_language: LanguageCode = LanguageCode.ENGLISH
    target_language: LanguageCode = LanguageCode.SWAHILI
    
    # Translation options
    preserve_formatting: bool = True
    context: Optional[str] = None
    domain: Optional[str] = None  # e.g., 'movie', 'technical', 'casual'
    max_length: Optional[int] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize request data."""
        if isinstance(self.source_language, str):
            self.source_language = LanguageCode(self.source_language)
        if isinstance(self.target_language, str):
            self.target_language = LanguageCode(self.target_language)


@dataclass
class TranslationResponse:
    """Response from translation service."""
    
    request_id: str
    translated_text: str
    source_text: str
    source_language: LanguageCode
    target_language: LanguageCode
    service: TranslationService
    
    # Quality metrics
    confidence_score: Optional[float] = None
    word_count: int = 0
    character_count: int = 0
    
    # Service metadata
    service_response_time: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    
    # Error handling
    error: Optional[str] = None
    success: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Calculate derived fields."""
        if self.translated_text:
            self.word_count = len(self.translated_text.split())
            self.character_count = len(self.translated_text)
        
        if isinstance(self.source_language, str):
            self.source_language = LanguageCode(self.source_language)
        if isinstance(self.target_language, str):
            self.target_language = LanguageCode(self.target_language)
        if isinstance(self.service, str):
            self.service = TranslationService(self.service)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "request_id": self.request_id,
            "translated_text": self.translated_text,
            "source_text": self.source_text,
            "source_language": self.source_language.value,
            "target_language": self.target_language.value,
            "service": self.service.value,
            "confidence_score": self.confidence_score,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "service_response_time": self.service_response_time,
            "tokens_used": self.tokens_used,
            "cost_estimate": self.cost_estimate,
            "error": self.error,
            "success": self.success,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class BatchTranslationRequest:
    """Request for batch translation of multiple texts."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    texts: List[str] = field(default_factory=list)
    source_language: LanguageCode = LanguageCode.ENGLISH
    target_language: LanguageCode = LanguageCode.SWAHILI
    
    # Batch options
    preserve_order: bool = True
    max_batch_size: int = 100
    parallel_processing: bool = True
    
    # Translation options
    preserve_formatting: bool = True
    context: Optional[str] = None
    domain: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_texts(self) -> int:
        """Get total number of texts to translate."""
        return len(self.texts)
    
    @property
    def total_characters(self) -> int:
        """Get total character count."""
        return sum(len(text) for text in self.texts)


@dataclass
class BatchTranslationResponse:
    """Response from batch translation service."""
    
    request_id: str
    translations: List[TranslationResponse]
    source_language: LanguageCode
    target_language: LanguageCode
    service: TranslationService
    
    # Batch metrics
    total_texts: int = 0
    successful_translations: int = 0
    failed_translations: int = 0
    total_processing_time: Optional[float] = None
    
    # Cost tracking
    total_tokens_used: Optional[int] = None
    total_cost_estimate: Optional[float] = None
    
    # Status
    completed: bool = False
    error: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Calculate derived metrics."""
        self.total_texts = len(self.translations)
        self.successful_translations = sum(1 for t in self.translations if t.success)
        self.failed_translations = self.total_texts - self.successful_translations
        
        if self.translations:
            self.total_tokens_used = sum(t.tokens_used or 0 for t in self.translations)
            self.total_cost_estimate = sum(t.cost_estimate or 0 for t in self.translations)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_texts == 0:
            return 0.0
        return (self.successful_translations / self.total_texts) * 100
    
    def get_successful_translations(self) -> List[TranslationResponse]:
        """Get only successful translations."""
        return [t for t in self.translations if t.success]
    
    def get_failed_translations(self) -> List[TranslationResponse]:
        """Get only failed translations."""
        return [t for t in self.translations if not t.success]


@dataclass
class SubtitleEntry:
    """Individual subtitle entry with timing information."""
    
    index: int
    start_time: str  # SRT format: "00:01:23,456"
    end_time: str    # SRT format: "00:01:25,789"
    text: str
    
    # Translation data
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    translation_confidence: Optional[float] = None
    
    # Metadata
    speaker: Optional[str] = None
    formatting_tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Extract formatting information."""
        if self.text:
            # Extract common subtitle formatting tags
            import re
            tags = re.findall(r'<[^>]+>', self.text)
            self.formatting_tags = tags
    
    @property
    def duration_ms(self) -> int:
        """Calculate duration in milliseconds."""
        start_ms = self._time_to_ms(self.start_time)
        end_ms = self._time_to_ms(self.end_time)
        return end_ms - start_ms
    
    def _time_to_ms(self, time_str: str) -> int:
        """Convert SRT time format to milliseconds."""
        try:
            # Format: "00:01:23,456"
            time_part, ms_part = time_str.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            
            return (h * 3600 + m * 60 + s) * 1000 + ms
        except (ValueError, IndexError):
            return 0
    
    def get_plain_text(self) -> str:
        """Get text without formatting tags."""
        import re
        return re.sub(r'<[^>]+>', '', self.text)
    
    def to_srt_format(self) -> str:
        """Convert back to SRT format."""
        text = self.translated_text if self.translated_text else self.text
        return f"{self.index}\n{self.start_time} --> {self.end_time}\n{text}\n"


@dataclass
class SubtitleFile:
    """Complete subtitle file with all entries."""
    
    entries: List[SubtitleEntry]
    source_language: LanguageCode = LanguageCode.ENGLISH
    target_language: Optional[LanguageCode] = None
    
    # File metadata
    filename: Optional[str] = None
    format_type: str = "srt"  # srt, ass, vtt, etc.
    encoding: str = "utf-8"
    
    # Translation metadata
    translation_service: Optional[TranslationService] = None
    translation_date: Optional[datetime] = None
    translation_quality_score: Optional[float] = None
    
    @property
    def total_entries(self) -> int:
        """Get total number of subtitle entries."""
        return len(self.entries)
    
    @property
    def total_duration_ms(self) -> int:
        """Get total duration of subtitle file."""
        if not self.entries:
            return 0
        return max(entry._time_to_ms(entry.end_time) for entry in self.entries)
    
    @property
    def is_translated(self) -> bool:
        """Check if subtitle file has been translated."""
        return any(entry.translated_text for entry in self.entries)
    
    def get_text_for_translation(self) -> List[str]:
        """Extract plain text from all entries for batch translation."""
        return [entry.get_plain_text() for entry in self.entries]
    
    def apply_translations(self, translations: List[str]) -> None:
        """Apply batch translations to subtitle entries."""
        if len(translations) != len(self.entries):
            raise ValueError("Number of translations must match number of entries")
        
        for entry, translation in zip(self.entries, translations):
            entry.translated_text = translation
    
    def to_srt_string(self, use_translation: bool = True) -> str:
        """Convert to SRT format string."""
        return "\n".join(
            entry.to_srt_format() for entry in self.entries
        ) + "\n"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get file statistics."""
        return {
            "total_entries": self.total_entries,
            "total_duration_ms": self.total_duration_ms,
            "total_characters": sum(len(entry.get_plain_text()) for entry in self.entries),
            "average_entry_length": sum(len(entry.get_plain_text()) for entry in self.entries) / max(1, self.total_entries),
            "is_translated": self.is_translated,
            "source_language": self.source_language.value,
            "target_language": self.target_language.value if self.target_language else None,
            "translation_service": self.translation_service.value if self.translation_service else None
        }


# Language mappings for different services
LANGUAGE_MAPPINGS = {
    TranslationService.GOOGLE_TRANSLATE: {
        LanguageCode.ENGLISH: "en",
        LanguageCode.SWAHILI: "sw",
        LanguageCode.SPANISH: "es",
        LanguageCode.FRENCH: "fr",
        LanguageCode.GERMAN: "de",
        LanguageCode.ARABIC: "ar",
        LanguageCode.PORTUGUESE: "pt",
        LanguageCode.ITALIAN: "it",
        LanguageCode.RUSSIAN: "ru",
        LanguageCode.CHINESE: "zh",
        LanguageCode.JAPANESE: "ja",
        LanguageCode.KOREAN: "ko",
        LanguageCode.HINDI: "hi"
    },
    TranslationService.OPENAI_GPT: {
        LanguageCode.ENGLISH: "English",
        LanguageCode.SWAHILI: "Swahili",
        LanguageCode.SPANISH: "Spanish",
        LanguageCode.FRENCH: "French",
        LanguageCode.GERMAN: "German",
        LanguageCode.ARABIC: "Arabic",
        LanguageCode.PORTUGUESE: "Portuguese",
        LanguageCode.ITALIAN: "Italian",
        LanguageCode.RUSSIAN: "Russian",
        LanguageCode.CHINESE: "Chinese",
        LanguageCode.JAPANESE: "Japanese",
        LanguageCode.KOREAN: "Korean",
        LanguageCode.HINDI: "Hindi"
    }
}


# Quality thresholds for translation confidence
QUALITY_THRESHOLDS = {
    "excellent": 0.95,
    "good": 0.80,
    "acceptable": 0.60,
    "poor": 0.40
}


def get_language_name(code: LanguageCode) -> str:
    """Get human-readable language name."""
    names = {
        LanguageCode.ENGLISH: "English",
        LanguageCode.SWAHILI: "Swahili",
        LanguageCode.SPANISH: "Spanish",
        LanguageCode.FRENCH: "French",
        LanguageCode.GERMAN: "German",
        LanguageCode.ARABIC: "Arabic",
        LanguageCode.PORTUGUESE: "Portuguese",
        LanguageCode.ITALIAN: "Italian",
        LanguageCode.RUSSIAN: "Russian",
        LanguageCode.CHINESE: "Chinese",
        LanguageCode.JAPANESE: "Japanese",
        LanguageCode.KOREAN: "Korean",
        LanguageCode.HINDI: "Hindi"
    }
    return names.get(code, code.value)
