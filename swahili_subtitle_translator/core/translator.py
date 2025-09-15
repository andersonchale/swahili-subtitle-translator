"""
Subtitle Translation Engine

Advanced subtitle translation with multiple service support, caching, and error handling.
"""

import time
import logging
import hashlib
from typing import Optional, Dict, List, Any
from pathlib import Path
import json

from deep_translator import GoogleTranslator, MyMemoryTranslator
from deep_translator.exceptions import TranslationNotFound, TooManyRequests, RequestError

from ..utils.cache import TranslationCache
from ..utils.exceptions import TranslationError, UnsupportedLanguageError

logger = logging.getLogger(__name__)


class TranslationService:
    """Translation service interface."""
    
    def __init__(self, source: str = 'en', target: str = 'sw'):
        self.source = source
        self.target = target
    
    def translate(self, text: str) -> str:
        """Translate text using the service."""
        raise NotImplementedError


class GoogleTranslationService(TranslationService):
    """Google Translate service wrapper."""
    
    def __init__(self, source: str = 'en', target: str = 'sw'):
        super().__init__(source, target)
        self.translator = GoogleTranslator(source=source, target=target)
        self.rate_limit_delay = 0.1
    
    def translate(self, text: str) -> str:
        """Translate text using Google Translate."""
        if not text.strip():
            return text
        
        try:
            result = self.translator.translate(text.strip())
            time.sleep(self.rate_limit_delay)  # Rate limiting
            return result
        except (TooManyRequests, RequestError) as e:
            logger.warning(f"Google Translate request failed: {e}")
            raise TranslationError(f"Translation service unavailable: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Google Translate: {e}")
            raise TranslationError(f"Translation failed: {e}")


class MyMemoryTranslationService(TranslationService):
    """MyMemory translation service wrapper."""
    
    def __init__(self, source: str = 'en', target: str = 'sw'):
        super().__init__(source, target)
        self.translator = MyMemoryTranslator(source=source, target=target)
        self.rate_limit_delay = 0.2
    
    def translate(self, text: str) -> str:
        """Translate text using MyMemory."""
        if not text.strip():
            return text
        
        try:
            result = self.translator.translate(text.strip())
            time.sleep(self.rate_limit_delay)  # Rate limiting
            return result
        except Exception as e:
            logger.warning(f"MyMemory translation failed: {e}")
            raise TranslationError(f"MyMemory translation failed: {e}")


class SubtitleTranslator:
    """
    Advanced subtitle translator with multiple services, caching, and error handling.
    
    Features:
    - Multiple translation services (Google Translate, MyMemory)
    - Translation caching for efficiency
    - Automatic fallback between services
    - Rate limiting and error handling
    - Progress tracking
    - Cultural adaptation for Swahili
    """
    
    def __init__(
        self,
        source_lang: str = 'en',
        target_lang: str = 'sw',
        cache_dir: Optional[Path] = None,
        primary_service: str = 'google',
        max_retries: int = 3,
        enable_cache: bool = True
    ):
        """
        Initialize the subtitle translator.
        
        Args:
            source_lang: Source language code (default: 'en')
            target_lang: Target language code (default: 'sw' for Swahili)
            cache_dir: Directory for translation cache
            primary_service: Primary translation service ('google' or 'mymemory')
            max_retries: Maximum retry attempts for failed translations
            enable_cache: Whether to enable translation caching
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.max_retries = max_retries
        self.enable_cache = enable_cache
        
        # Initialize translation services
        self.services = {
            'google': GoogleTranslationService(source_lang, target_lang)
        }
        
        # Try to initialize MyMemory with proper language codes
        try:
            # MyMemory uses different language codes
            mymemory_source = 'english' if source_lang == 'en' else source_lang
            mymemory_target = 'swahili' if target_lang == 'sw' else target_lang
            self.services['mymemory'] = MyMemoryTranslationService(mymemory_source, mymemory_target)
            logger.info("MyMemory translation service initialized successfully")
        except Exception as e:
            logger.warning(f"MyMemory service initialization failed: {e}")
            logger.info("Continuing with Google Translate only")
        
        # Set primary and fallback services
        if primary_service not in self.services:
            # If requested service is not available, fall back to available services
            available_services = list(self.services.keys())
            if available_services:
                primary_service = available_services[0]
                logger.warning(f"Requested service not available, using {primary_service}")
            else:
                raise ValueError("No translation services available")
        
        self.primary_service = primary_service
        self.fallback_services = [s for s in self.services.keys() if s != primary_service]
        
        # Initialize cache
        if enable_cache:
            cache_path = cache_dir or Path.home() / '.swahili_subtitle_translator' / 'cache'
            self.cache = TranslationCache(cache_path)
        else:
            self.cache = None
        
        # Translation statistics
        self.stats = {
            'total_translations': 0,
            'cache_hits': 0,
            'service_usage': {service: 0 for service in self.services.keys()},
            'failed_translations': 0
        }
        
        logger.info(f"Initialized SubtitleTranslator: {source_lang} -> {target_lang}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        combined = f"{self.source_lang}:{self.target_lang}:{text}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before translation.
        
        Handles special cases like character names, places, etc.
        """
        # Keep original for now, but this could be expanded for:
        # - Character name preservation
        # - Cultural context adaptation
        # - Technical term handling
        return text.strip()
    
    def _postprocess_text(self, text: str, original: str) -> str:
        """
        Post-process translated text.
        
        Apply cultural adaptations and corrections specific to Swahili.
        """
        # Basic post-processing - can be expanded
        processed = text.strip()
        
        # Common English->Swahili adaptations
        adaptations = {
            'Your Grace': 'Neema yako',
            'My Lord': 'Bwana wangu',
            'My Lady': 'Bibi wangu',
            'Your Majesty': 'Mfalme wangu',
            'the North': 'Kaskazini',
            'the South': 'Kusini',
            'Winter is coming': 'Baridi inakuja'
        }
        
        for eng, swa in adaptations.items():
            if eng.lower() in original.lower():
                processed = processed.replace(eng, swa)
        
        return processed
    
    def translate_text(self, text: str, progress_callback=None) -> str:
        """
        Translate a single text string.
        
        Args:
            text: Text to translate
            progress_callback: Optional callback for progress updates
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        self.stats['total_translations'] += 1
        
        # Check cache first
        if self.cache:
            cache_key = self._get_cache_key(text)
            cached = self.cache.get(cache_key)
            if cached:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit for: {text[:50]}...")
                return cached
        
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Handle long text by splitting into sentences (improved from original)
        if len(processed_text) > 500:
            return self._translate_long_text(processed_text, text, progress_callback)
        
        # Translate normal length text
        return self._translate_single_text(processed_text, text, progress_callback)
    
    def _translate_long_text(self, processed_text: str, original_text: str, progress_callback=None) -> str:
        """
        Translate long text by splitting into sentences.
        
        Improved version of the original script's sentence splitting logic.
        """
        logger.debug(f"Translating long text ({len(processed_text)} chars): {processed_text[:50]}...")
        
        # Split by sentences - improved detection
        sentence_delimiters = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        sentences = [processed_text]
        
        for delimiter in sentence_delimiters:
            new_sentences = []
            for sentence in sentences:
                new_sentences.extend(sentence.split(delimiter))
            sentences = [s.strip() for s in new_sentences if s.strip()]
        
        if len(sentences) <= 1:
            # Fallback: split by punctuation if no sentences found
            sentences = [s.strip() for s in processed_text.split(',') if s.strip()]
        
        if len(sentences) <= 1:
            # Last resort: translate as single text
            return self._translate_single_text(processed_text, original_text, progress_callback)
        
        # Translate each sentence
        translated_sentences = []
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                logger.debug(f"Translating sentence {i+1}/{len(sentences)}: {sentence[:30]}...")
                translated = self._translate_single_text(sentence.strip(), sentence, progress_callback)
                translated_sentences.append(translated)
                # Small delay between sentence translations
                time.sleep(0.1)
        
        # Reconstruct the text with proper punctuation
        result = '. '.join(translated_sentences)
        
        # Apply post-processing
        final_result = self._postprocess_text(result, original_text)
        
        # Cache the result
        if self.cache:
            cache_key = self._get_cache_key(original_text)
            self.cache.set(cache_key, final_result, original_text, self.source_lang, self.target_lang)
        
        return final_result
    
    def _translate_single_text(self, processed_text: str, original_text: str, progress_callback=None) -> str:
        """
        Translate a single piece of text using available services.
        """
        # Try translation with services
        services_to_try = [self.primary_service] + self.fallback_services
        last_error = None
        
        for service_name in services_to_try:
            service = self.services[service_name]
            
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"Translating with {service_name} (attempt {attempt + 1}): {original_text[:50]}...")
                    
                    translated = service.translate(processed_text)
                    
                    if translated and translated.strip():
                        # Post-process translation
                        final_translation = self._postprocess_text(translated, original_text)
                        
                        # Cache the result
                        if self.cache:
                            cache_key = self._get_cache_key(original_text)
                            self.cache.set(cache_key, final_translation, original_text, self.source_lang, self.target_lang)
                        
                        # Update stats
                        self.stats['service_usage'][service_name] += 1
                        
                        logger.debug(f"Successfully translated: {original_text[:30]}... -> {final_translation[:30]}...")
                        
                        if progress_callback:
                            progress_callback(1)
                        
                        return final_translation
                
                except TranslationError as e:
                    last_error = e
                    logger.warning(f"{service_name} failed (attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    break  # Try next service
                
                except Exception as e:
                    last_error = e
                    logger.error(f"Unexpected error with {service_name}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2)
        
        # If all services failed, return original text
        self.stats['failed_translations'] += 1
        logger.error(f"All translation services failed for: {original_text[:50]}...")
        
        if progress_callback:
            progress_callback(1)
        
        return original_text  # Return original text as fallback
    
    def translate_batch(
        self,
        texts: List[str],
        progress_callback=None,
        batch_size: int = 10
    ) -> List[str]:
        """
        Translate multiple texts efficiently.
        
        Args:
            texts: List of texts to translate
            progress_callback: Progress callback function
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of translated texts
        """
        results = []
        total = len(texts)
        
        for i, text in enumerate(texts):
            translated = self.translate_text(text)
            results.append(translated)
            
            if progress_callback:
                progress_callback(i + 1, total)
            
            # Small delay between translations to avoid rate limiting
            if i < total - 1:
                time.sleep(0.1)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get translation statistics."""
        stats = self.stats.copy()
        
        if stats['total_translations'] > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / stats['total_translations']
            stats['success_rate'] = (
                (stats['total_translations'] - stats['failed_translations']) 
                / stats['total_translations']
            )
        else:
            stats['cache_hit_rate'] = 0.0
            stats['success_rate'] = 0.0
        
        return stats
    
    def clear_cache(self):
        """Clear translation cache."""
        if self.cache:
            self.cache.clear()
            logger.info("Translation cache cleared")
    
    def save_cache(self):
        """Save translation cache to disk."""
        if self.cache:
            self.cache.save()
            logger.info("Translation cache saved")
