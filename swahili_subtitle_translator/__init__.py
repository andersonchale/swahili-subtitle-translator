"""
Swahili Subtitle Translator

A powerful, open-source tool for translating subtitle files from English to Swahili.
Supports multiple subtitle formats and provides both CLI and programmatic interfaces.

Author: Anderson
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Anderson"
__license__ = "MIT"
__description__ = "Professional subtitle translation tool for English to Swahili"

# Import main components from our new implementation
from .search import SubtitleSearchEngine, search_subtitles
from .translation import (
    TranslationEngine, 
    create_translation_engine, 
    translate_simple,
    parse_srt_file,
    save_srt_file
)
from .config import get_config_manager, get_config

__all__ = [
    # Search functionality
    "SubtitleSearchEngine", 
    "search_subtitles",
    
    # Translation functionality
    "TranslationEngine", 
    "create_translation_engine", 
    "translate_simple",
    "parse_srt_file",
    "save_srt_file",
    
    # Configuration
    "get_config_manager", 
    "get_config",
    
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    "__description__"
]
