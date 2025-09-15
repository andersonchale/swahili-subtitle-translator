"""
Custom exceptions for subtitle translation.
"""


class SubtitleTranslatorError(Exception):
    """Base exception for subtitle translator."""
    pass


class TranslationError(SubtitleTranslatorError):
    """Exception raised when translation fails."""
    pass


class UnsupportedLanguageError(SubtitleTranslatorError):
    """Exception raised when language is not supported."""
    pass


class UnsupportedFormatError(SubtitleTranslatorError):
    """Exception raised when subtitle format is not supported."""
    pass


class SubtitleProcessingError(SubtitleTranslatorError):
    """Exception raised when subtitle processing fails."""
    pass


class CacheError(SubtitleTranslatorError):
    """Exception raised when cache operations fail."""
    pass


class ConfigurationError(SubtitleTranslatorError):
    """Exception raised when configuration is invalid."""
    pass
