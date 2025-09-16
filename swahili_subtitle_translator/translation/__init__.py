"""
Translation module for subtitle translation functionality.
"""

# Core models
from .models import (
    TranslationRequest,
    TranslationResponse,
    BatchTranslationRequest,
    BatchTranslationResponse,
    TranslationService,
    LanguageCode,
    SubtitleEntry,
    SubtitleFile,
    LANGUAGE_MAPPINGS,
    QUALITY_THRESHOLDS,
    get_language_name
)

# Translation services
from .services import (
    BaseTranslationService,
    GoogleTranslateService,
    OpenAITranslationService,
    MockTranslationService,
    OfflineTranslationService,
    TranslationServiceError,
    create_translation_service,
    translate_text
)

# Translation engine
from .engine import (
    TranslationEngine,
    TranslationEngineError,
    create_translation_engine,
    translate_simple
)

# Subtitle parsing
from .subtitle_parser import (
    SRTParser,
    SubtitleValidator,
    SubtitleProcessor,
    SubtitleParserError,
    parse_srt_file,
    save_srt_file,
    create_sample_subtitles
)

__all__ = [
    # Models
    "TranslationRequest",
    "TranslationResponse", 
    "BatchTranslationRequest",
    "BatchTranslationResponse",
    "TranslationService",
    "LanguageCode",
    "SubtitleEntry",
    "SubtitleFile",
    "LANGUAGE_MAPPINGS",
    "QUALITY_THRESHOLDS",
    "get_language_name",
    
    # Services
    "BaseTranslationService",
    "GoogleTranslateService",
    "OpenAITranslationService", 
    "MockTranslationService",
    "OfflineTranslationService",
    "TranslationServiceError",
    "create_translation_service",
    "translate_text",
    
    # Engine
    "TranslationEngine",
    "TranslationEngineError",
    "create_translation_engine", 
    "translate_simple",
    
    # Subtitle parsing
    "SRTParser",
    "SubtitleValidator",
    "SubtitleProcessor",
    "SubtitleParserError",
    "parse_srt_file",
    "save_srt_file",
    "create_sample_subtitles"
]
