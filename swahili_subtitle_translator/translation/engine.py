"""
Translation engine that coordinates multiple translation services.
"""

import logging
from typing import List, Dict, Optional, Union, Callable
from datetime import datetime
import time

from .models import (
    TranslationRequest,
    TranslationResponse,
    BatchTranslationRequest,
    BatchTranslationResponse,
    TranslationService,
    LanguageCode,
    SubtitleFile,
    QUALITY_THRESHOLDS
)
from .services import (
    BaseTranslationService,
    create_translation_service,
    TranslationServiceError
)
from ..utils.exceptions import SubtitleTranslatorError

logger = logging.getLogger(__name__)


class TranslationEngineError(SubtitleTranslatorError):
    """Exception raised by translation engine."""
    pass


class TranslationEngine:
    """
    Main translation engine that coordinates multiple translation services.
    
    Provides intelligent fallbacks, quality assessment, and cost optimization.
    """
    
    def __init__(self, 
                 service_configs: Optional[Dict[TranslationService, Dict]] = None,
                 default_service: TranslationService = TranslationService.GOOGLE_TRANSLATE,
                 fallback_services: Optional[List[TranslationService]] = None,
                 quality_threshold: float = 0.6):
        """
        Initialize the translation engine.
        
        Args:
            service_configs: Configuration for each service
            default_service: Primary service to use
            fallback_services: Services to try if primary fails
            quality_threshold: Minimum acceptable translation quality
        """
        self.service_configs = service_configs or {}
        self.default_service = default_service
        self.fallback_services = fallback_services or [TranslationService.OFFLINE_MODEL, TranslationService.MOCK]
        self.quality_threshold = quality_threshold
        
        # Service instances
        self.services: Dict[TranslationService, BaseTranslationService] = {}
        
        # Statistics
        self.translation_stats = {
            'total_translations': 0,
            'successful_translations': 0,
            'failed_translations': 0,
            'fallback_used': 0,
            'total_cost': 0.0,
            'average_quality': 0.0,
            'service_usage': {}
        }
        
        self._initialize_services()
        
        logger.info(f"Translation engine initialized with primary service: {default_service.value}")
    
    def _initialize_services(self):
        """Initialize translation services based on configuration."""
        # Always initialize mock service as ultimate fallback
        self.services[TranslationService.MOCK] = create_translation_service(
            TranslationService.MOCK
        )
        
        # Initialize configured services
        for service_type, config in self.service_configs.items():
            try:
                service = create_translation_service(service_type, **config)
                self.services[service_type] = service
                logger.info(f"Initialized {service_type.value} service")
            except Exception as e:
                logger.error(f"Failed to initialize {service_type.value}: {e}")
        
        # Always try to initialize Google Translate if not already configured (free service)
        if TranslationService.GOOGLE_TRANSLATE not in self.services:
            try:
                service = create_translation_service(TranslationService.GOOGLE_TRANSLATE)
                self.services[TranslationService.GOOGLE_TRANSLATE] = service
                logger.info(f"Initialized {TranslationService.GOOGLE_TRANSLATE.value} service")
            except Exception as e:
                logger.warning(f"Google Translate not available: {e}")
        
        # Ensure default service is available
        if self.default_service not in self.services:
            logger.warning(f"Default service {self.default_service.value} not available, using mock")
            self.default_service = TranslationService.MOCK
    
    def translate(self, 
                 request: Union[TranslationRequest, str],
                 preferred_service: Optional[TranslationService] = None,
                 use_fallbacks: bool = True) -> TranslationResponse:
        """
        Translate a single text with intelligent fallbacks.
        
        Args:
            request: Translation request or plain text
            preferred_service: Preferred service to use
            use_fallbacks: Whether to use fallback services
            
        Returns:
            Translation response
        """
        # Convert string to TranslationRequest if needed
        if isinstance(request, str):
            request = TranslationRequest(text=request)
        
        # Determine service order
        services_to_try = self._get_service_order(preferred_service, use_fallbacks)
        
        last_error = None
        for service_type in services_to_try:
            if service_type not in self.services:
                continue
            
            try:
                service = self.services[service_type]
                logger.info(f"Attempting translation with {service_type.value}")
                
                response = service.translate(request)
                
                if response.success and self._is_quality_acceptable(response):
                    # Update statistics
                    self._update_stats(response, service_type, is_fallback=service_type != self.default_service)
                    return response
                else:
                    logger.warning(f"Translation quality below threshold or failed: {service_type.value}")
                    last_error = response.error or "Quality below threshold"
                    
            except Exception as e:
                logger.error(f"Service {service_type.value} failed: {e}")
                last_error = str(e)
                continue
        
        # All services failed
        self.translation_stats['failed_translations'] += 1
        
        error_response = TranslationResponse(
            request_id=request.id,
            translated_text="",
            source_text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            service=self.default_service,
            error=f"All translation services failed. Last error: {last_error}",
            success=False
        )
        
        return error_response
    
    def translate_batch(self,
                       request: Union[BatchTranslationRequest, List[str]],
                       preferred_service: Optional[TranslationService] = None,
                       use_fallbacks: bool = True,
                       progress_callback: Optional[Callable[[int, int], None]] = None) -> BatchTranslationResponse:
        """
        Translate multiple texts with progress tracking.
        
        Args:
            request: Batch request or list of texts
            preferred_service: Preferred service to use
            use_fallbacks: Whether to use fallback services
            progress_callback: Callback for progress updates
            
        Returns:
            Batch translation response
        """
        start_time = time.time()
        
        # Convert list to BatchTranslationRequest if needed
        if isinstance(request, list):
            request = BatchTranslationRequest(texts=request)
        
        logger.info(f"Starting batch translation of {len(request.texts)} texts")
        
        # Determine primary service
        service_type = preferred_service or self.default_service
        if service_type not in self.services:
            service_type = TranslationService.MOCK
        
        service = self.services[service_type]
        
        try:
            # Use service's batch translation if available
            response = service.translate_batch(request)
            
            # If some translations failed and fallbacks are enabled, retry failed ones
            if use_fallbacks and response.failed_translations > 0:
                response = self._retry_failed_translations(response, request)
            
            # Update statistics
            for translation in response.translations:
                if translation.success:
                    self._update_stats(translation, translation.service, is_fallback=False)
                else:
                    self.translation_stats['failed_translations'] += 1
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(response.successful_translations, response.total_texts)
            
            processing_time = time.time() - start_time
            response.total_processing_time = processing_time
            
            logger.info(f"Batch translation completed: {response.successful_translations}/{response.total_texts} successful")
            
            return response
            
        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
            
            # Return error response
            return BatchTranslationResponse(
                request_id=request.id,
                translations=[],
                source_language=request.source_language,
                target_language=request.target_language,
                service=service_type,
                error=str(e),
                completed=True,
                completed_at=datetime.now()
            )
    
    def translate_subtitle_file(self,
                               subtitle_file: SubtitleFile,
                               target_language: LanguageCode = LanguageCode.SWAHILI,
                               preferred_service: Optional[TranslationService] = None,
                               progress_callback: Optional[Callable[[int, int], None]] = None) -> SubtitleFile:
        """
        Translate an entire subtitle file.
        
        Args:
            subtitle_file: Subtitle file to translate
            target_language: Target language for translation
            preferred_service: Preferred service to use
            progress_callback: Progress callback function
            
        Returns:
            Translated subtitle file
        """
        logger.info(f"Translating subtitle file with {subtitle_file.total_entries} entries")
        
        # Extract texts for translation
        texts = subtitle_file.get_text_for_translation()
        
        # Create batch request
        batch_request = BatchTranslationRequest(
            texts=texts,
            source_language=subtitle_file.source_language,
            target_language=target_language,
            domain="movie",  # Subtitle context
            preserve_formatting=True
        )
        
        # Translate batch
        batch_response = self.translate_batch(
            batch_request, 
            preferred_service=preferred_service,
            progress_callback=progress_callback
        )
        
        # Apply successful translations
        successful_translations = batch_response.get_successful_translations()
        if successful_translations:
            translated_texts = [t.translated_text for t in successful_translations]
            
            # Handle partial failures by filling gaps with original text
            if len(translated_texts) < len(texts):
                logger.warning(f"Some translations failed, using original text for {len(texts) - len(translated_texts)} entries")
                complete_translations = []
                success_index = 0
                
                for i, original_text in enumerate(texts):
                    if success_index < len(successful_translations) and successful_translations[success_index].source_text == original_text:
                        complete_translations.append(successful_translations[success_index].translated_text)
                        success_index += 1
                    else:
                        complete_translations.append(original_text)  # Use original if translation failed
                
                translated_texts = complete_translations
            
            subtitle_file.apply_translations(translated_texts)
            subtitle_file.target_language = target_language
            subtitle_file.translation_service = batch_response.service
            subtitle_file.translation_date = datetime.now()
            
            # Calculate quality score
            quality_scores = [t.confidence_score for t in successful_translations if t.confidence_score]
            if quality_scores:
                subtitle_file.translation_quality_score = sum(quality_scores) / len(quality_scores)
        
        logger.info(f"Subtitle translation completed with {batch_response.success_rate:.1f}% success rate")
        
        return subtitle_file
    
    def _get_service_order(self, 
                          preferred_service: Optional[TranslationService],
                          use_fallbacks: bool) -> List[TranslationService]:
        """Get ordered list of services to try."""
        services = []
        
        # Add preferred service first
        if preferred_service and preferred_service in self.services:
            services.append(preferred_service)
        elif self.default_service in self.services:
            services.append(self.default_service)
        
        # Add fallback services if enabled
        if use_fallbacks:
            for service in self.fallback_services:
                if service not in services and service in self.services:
                    services.append(service)
        
        # Ensure mock service is last resort
        if TranslationService.MOCK not in services:
            services.append(TranslationService.MOCK)
        
        return services
    
    def _is_quality_acceptable(self, response: TranslationResponse) -> bool:
        """Check if translation quality is acceptable."""
        if not response.success:
            return False
        
        if response.confidence_score is None:
            return True  # No confidence score available, assume acceptable
        
        return response.confidence_score >= self.quality_threshold
    
    def _retry_failed_translations(self,
                                 response: BatchTranslationResponse,
                                 original_request: BatchTranslationRequest) -> BatchTranslationResponse:
        """Retry failed translations with fallback services."""
        failed_translations = response.get_failed_translations()
        if not failed_translations:
            return response
        
        logger.info(f"Retrying {len(failed_translations)} failed translations with fallback services")
        
        # Get fallback services
        fallback_services = [s for s in self.fallback_services if s in self.services and s != response.service]
        
        for service_type in fallback_services:
            if not failed_translations:
                break  # All failures resolved
            
            service = self.services[service_type]
            remaining_failures = []
            
            for failed_translation in failed_translations:
                try:
                    # Create new request
                    retry_request = TranslationRequest(
                        text=failed_translation.source_text,
                        source_language=failed_translation.source_language,
                        target_language=failed_translation.target_language
                    )
                    
                    # Retry translation
                    retry_response = service.translate(retry_request)
                    
                    if retry_response.success and self._is_quality_acceptable(retry_response):
                        # Replace failed translation with successful one
                        for i, translation in enumerate(response.translations):
                            if translation.request_id == failed_translation.request_id:
                                response.translations[i] = retry_response
                                self.translation_stats['fallback_used'] += 1
                                break
                    else:
                        remaining_failures.append(failed_translation)
                        
                except Exception as e:
                    logger.error(f"Fallback translation failed: {e}")
                    remaining_failures.append(failed_translation)
            
            failed_translations = remaining_failures
        
        # Recalculate batch metrics
        response.__post_init__()
        
        return response
    
    def _update_stats(self, response: TranslationResponse, service_type: TranslationService, is_fallback: bool):
        """Update translation statistics."""
        self.translation_stats['total_translations'] += 1
        
        if response.success:
            self.translation_stats['successful_translations'] += 1
            
            if response.confidence_score:
                # Update average quality
                current_avg = self.translation_stats['average_quality']
                total = self.translation_stats['successful_translations']
                self.translation_stats['average_quality'] = ((current_avg * (total - 1)) + response.confidence_score) / total
        
        if is_fallback:
            self.translation_stats['fallback_used'] += 1
        
        if response.cost_estimate:
            self.translation_stats['total_cost'] += response.cost_estimate
        
        # Update service usage stats
        service_key = service_type.value
        if service_key not in self.translation_stats['service_usage']:
            self.translation_stats['service_usage'][service_key] = 0
        self.translation_stats['service_usage'][service_key] += 1
    
    def get_available_services(self) -> List[TranslationService]:
        """Get list of available translation services."""
        return list(self.services.keys())
    
    def get_service_info(self, service_type: TranslationService) -> Optional[Dict]:
        """Get information about a specific service."""
        if service_type in self.services:
            return self.services[service_type].get_service_info()
        return None
    
    def get_engine_stats(self) -> Dict:
        """Get translation engine statistics."""
        stats = self.translation_stats.copy()
        stats['available_services'] = [s.value for s in self.get_available_services()]
        stats['default_service'] = self.default_service.value
        stats['quality_threshold'] = self.quality_threshold
        return stats
    
    def test_services(self, test_text: str = "Hello world") -> Dict[TranslationService, bool]:
        """Test all available services with a simple translation."""
        results = {}
        
        test_request = TranslationRequest(
            text=test_text,
            source_language=LanguageCode.ENGLISH,
            target_language=LanguageCode.SWAHILI
        )
        
        for service_type in self.services:
            try:
                service = self.services[service_type]
                response = service.translate(test_request)
                results[service_type] = response.success
                logger.info(f"Service test {service_type.value}: {'✓' if response.success else '✗'}")
            except Exception as e:
                results[service_type] = False
                logger.error(f"Service test {service_type.value}: ✗ ({e})")
        
        return results
    
    def set_quality_threshold(self, threshold: float):
        """Set the minimum acceptable quality threshold."""
        if not 0 <= threshold <= 1:
            raise ValueError("Quality threshold must be between 0 and 1")
        
        self.quality_threshold = threshold
        logger.info(f"Quality threshold updated to {threshold}")
    
    def add_service(self, service_type: TranslationService, config: Dict):
        """Add or update a translation service."""
        try:
            service = create_translation_service(service_type, **config)
            self.services[service_type] = service
            self.service_configs[service_type] = config
            logger.info(f"Added/updated service: {service_type.value}")
        except Exception as e:
            logger.error(f"Failed to add service {service_type.value}: {e}")
            raise TranslationEngineError(f"Failed to add service: {e}")


# Convenience functions
def create_translation_engine(google_api_key: Optional[str] = None,
                            openai_api_key: Optional[str] = None,
                            default_service: TranslationService = TranslationService.GOOGLE_TRANSLATE) -> TranslationEngine:
    """
    Create a translation engine with common services.
    
    Args:
        google_api_key: Google Translate API key
        openai_api_key: OpenAI API key
        default_service: Default service to use
        
    Returns:
        Configured translation engine
    """
    service_configs = {}
    
    # Always add Google Translate (free with deep-translator)
    service_configs[TranslationService.GOOGLE_TRANSLATE] = {}
    
    if openai_api_key:
        service_configs[TranslationService.OPENAI_GPT] = {
            'api_key': openai_api_key
        }
    
    # Add offline service
    service_configs[TranslationService.OFFLINE_MODEL] = {}
    
    fallbacks = [TranslationService.GOOGLE_TRANSLATE, TranslationService.OFFLINE_MODEL, TranslationService.MOCK]
    
    return TranslationEngine(
        service_configs=service_configs,
        default_service=default_service,
        fallback_services=fallbacks
    )


def translate_simple(text: str,
                    target_language: LanguageCode = LanguageCode.SWAHILI,
                    **kwargs) -> str:
    """
    Simple translation function for quick use.
    
    Args:
        text: Text to translate
        target_language: Target language
        **kwargs: Additional configuration
        
    Returns:
        Translated text
    """
    engine = create_translation_engine(**kwargs)
    response = engine.translate(text)
    return response.translated_text if response.success else text
