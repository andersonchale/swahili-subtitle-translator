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

from .core.translator import SubtitleTranslator
from .core.processor import SubtitleProcessor
from .utils.formats import SupportedFormats

__all__ = [
    "SubtitleTranslator",
    "SubtitleProcessor", 
    "SupportedFormats",
    "__version__"
]
