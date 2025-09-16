"""
Translation service implementations for different providers.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import json
import requests
from datetime import datetime

# Try to import deep-translator
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False

from .models import (
    TranslationRequest, 
    TranslationResponse, 
    BatchTranslationRequest,
    BatchTranslationResponse,
    TranslationService,
    LanguageCode,
    LANGUAGE_MAPPINGS
)
from ..utils.exceptions import SubtitleTranslatorError

logger = logging.getLogger(__name__)


class TranslationServiceError(SubtitleTranslatorError):
    """Exception raised by translation services."""
    pass


class BaseTranslationService(ABC):
    """Abstract base class for translation services."""
    
    def __init__(self, service_type: TranslationService, **kwargs):
        """
        Initialize translation service.
        
        Args:
            service_type: Type of translation service
            **kwargs: Service-specific configuration
        """
        self.service_type = service_type
        self.config = kwargs
        self.session = requests.Session()
        
        # Rate limiting
        self.rate_limit = kwargs.get('rate_limit', 1.0)
        self._last_request_time = 0
        
        # Cost tracking
        self.total_characters_translated = 0
        self.total_cost = 0.0
        
        logger.info(f"Initialized {service_type.value} translation service")
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request_time = time.time()
    
    def _get_service_language_code(self, language: LanguageCode) -> str:
        """Get service-specific language code."""
        mapping = LANGUAGE_MAPPINGS.get(self.service_type, {})
        return mapping.get(language, language.value)
    
    @abstractmethod
    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """
        Translate a single text request.
        
        Args:
            request: Translation request
            
        Returns:
            Translation response
        """
        pass
    
    def translate_batch(self, request: BatchTranslationRequest) -> BatchTranslationResponse:
        """
        Translate multiple texts in batch.
        
        Default implementation processes requests sequentially.
        Services can override for true batch processing.
        
        Args:
            request: Batch translation request
            
        Returns:
            Batch translation response
        """
        start_time = time.time()
        translations = []
        
        logger.info(f"Starting batch translation of {len(request.texts)} texts")
        
        for i, text in enumerate(request.texts):
            try:
                # Create individual request
                individual_request = TranslationRequest(
                    text=text,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    preserve_formatting=request.preserve_formatting,
                    context=request.context,
                    domain=request.domain
                )
                
                # Translate
                response = self.translate(individual_request)
                translations.append(response)
                
                if (i + 1) % 10 == 0:  # Log progress every 10 translations
                    logger.info(f"Completed {i + 1}/{len(request.texts)} translations")
                    
            except Exception as e:
                # Create error response
                error_response = TranslationResponse(
                    request_id=individual_request.id,
                    translated_text="",
                    source_text=text,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    service=self.service_type,
                    error=str(e),
                    success=False
                )
                translations.append(error_response)
                logger.error(f"Translation failed for text {i}: {e}")
        
        processing_time = time.time() - start_time
        
        return BatchTranslationResponse(
            request_id=request.id,
            translations=translations,
            source_language=request.source_language,
            target_language=request.target_language,
            service=self.service_type,
            total_processing_time=processing_time,
            completed=True,
            completed_at=datetime.now()
        )
    
    def get_supported_languages(self) -> List[LanguageCode]:
        """Get list of supported languages."""
        mapping = LANGUAGE_MAPPINGS.get(self.service_type, {})
        return list(mapping.keys())
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "service_type": self.service_type.value,
            "supported_languages": [lang.value for lang in self.get_supported_languages()],
            "rate_limit": self.rate_limit,
            "total_characters_translated": self.total_characters_translated,
            "total_cost": self.total_cost
        }


class GoogleTranslateService(BaseTranslationService):
    """Google Translate service using deep-translator (free)."""
    
    def __init__(self, **kwargs):
        """
        Initialize Google Translate service.
        No API key required - uses deep-translator.
        """
        super().__init__(TranslationService.GOOGLE_TRANSLATE, **kwargs)
        
        if not DEEP_TRANSLATOR_AVAILABLE:
            raise TranslationServiceError("deep-translator package not available")
        
        self.translator = None
    
    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate using Google Translate via deep-translator."""
        start_time = time.time()
        
        try:
            self._rate_limit_wait()
            
            source_lang = self._get_service_language_code(request.source_language)
            target_lang = self._get_service_language_code(request.target_language)
            
            # Create translator instance
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Translate text
            translated_text = translator.translate(request.text)
            
            if not translated_text:
                raise TranslationServiceError("Empty translation result")
            
            # Update totals
            char_count = len(request.text)
            self.total_characters_translated += char_count
            
            service_time = time.time() - start_time
            
            return TranslationResponse(
                request_id=request.id,
                translated_text=translated_text,
                source_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                service=self.service_type,
                confidence_score=0.85,  # Assume high confidence for Google
                service_response_time=service_time,
                cost_estimate=0.0,  # Free service
                completed_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Google Translate service error: {e}")
            return TranslationResponse(
                request_id=request.id,
                translated_text="",
                source_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                service=self.service_type,
                error=str(e),
                success=False
            )


class OpenAITranslationService(BaseTranslationService):
    """OpenAI GPT-based translation service."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        """
        Initialize OpenAI translation service.
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use
        """
        super().__init__(TranslationService.OPENAI_GPT, **kwargs)
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        # Set headers
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        
        # Cost per token (approximate for gpt-3.5-turbo)
        self.cost_per_input_token = 0.0015 / 1000  # $1.50 per 1K input tokens
        self.cost_per_output_token = 0.002 / 1000   # $2.00 per 1K output tokens
    
    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate using OpenAI GPT."""
        start_time = time.time()
        
        try:
            self._rate_limit_wait()
            
            source_lang = self._get_service_language_code(request.source_language)
            target_lang = self._get_service_language_code(request.target_language)
            
            # Create context-aware prompt
            system_prompt = self._create_system_prompt(source_lang, target_lang, request)
            user_prompt = f"Translate this text: \"{request.text}\""
            
            # Prepare request
            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'max_tokens': min(len(request.text) * 2, 4000),  # Reasonable limit
                'temperature': 0.1  # Low temperature for consistent translations
            }
            
            # Make request
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                raise TranslationServiceError("Invalid response from OpenAI")
            
            translated_text = result['choices'][0]['message']['content'].strip()
            
            # Remove quotes if GPT added them
            if translated_text.startswith('"') and translated_text.endswith('"'):
                translated_text = translated_text[1:-1]
            
            # Calculate cost and token usage
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', input_tokens + output_tokens)
            
            cost = (input_tokens * self.cost_per_input_token + 
                   output_tokens * self.cost_per_output_token)
            
            # Update totals
            self.total_characters_translated += len(request.text)
            self.total_cost += cost
            
            service_time = time.time() - start_time
            
            return TranslationResponse(
                request_id=request.id,
                translated_text=translated_text,
                source_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                service=self.service_type,
                confidence_score=0.90,  # GPT generally produces high-quality translations
                service_response_time=service_time,
                tokens_used=total_tokens,
                cost_estimate=cost,
                completed_at=datetime.now()
            )
            
        except requests.RequestException as e:
            logger.error(f"OpenAI API request failed: {e}")
            return TranslationResponse(
                request_id=request.id,
                translated_text="",
                source_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                service=self.service_type,
                error=f"API request failed: {e}",
                success=False
            )
        except Exception as e:
            logger.error(f"OpenAI translation service error: {e}")
            return TranslationResponse(
                request_id=request.id,
                translated_text="",
                source_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                service=self.service_type,
                error=str(e),
                success=False
            )
    
    def _create_system_prompt(self, source_lang: str, target_lang: str, 
                            request: TranslationRequest) -> str:
        """Create context-aware system prompt for GPT."""
        prompt = f"""You are a professional translator specializing in {source_lang} to {target_lang} translation."""
        
        if request.domain:
            prompt += f"\n\nContext: This text is from {request.domain} content."
        
        if request.context:
            prompt += f"\n\nAdditional context: {request.context}"
        
        prompt += f"""

Guidelines:
- Provide accurate, natural translations that preserve the original meaning
- Maintain the tone and style appropriate for the content
- Keep cultural nuances in mind
- For subtitle content, keep translations concise while preserving meaning
- Return ONLY the translated text, nothing else
- Do not add explanations or commentary
"""
        
        if request.preserve_formatting:
            prompt += "\n- Preserve any HTML tags or special formatting in the original text"
        
        return prompt


class MockTranslationService(BaseTranslationService):
    """Mock translation service for testing."""
    
    def __init__(self, **kwargs):
        """Initialize mock translation service."""
        super().__init__(TranslationService.MOCK, **kwargs)
        
        # Predefined translations for testing
        self.mock_translations = {
            ("Hello", "en", "sw"): "Hujambo",
            ("How are you?", "en", "sw"): "Hujambo?",
            ("Good morning", "en", "sw"): "Habari za asubuhi",
            ("Thank you", "en", "sw"): "Asante",
            ("Welcome", "en", "sw"): "Karibu",
            ("I love you", "en", "sw"): "Nakupenda",
            ("What is your name?", "en", "sw"): "Jina lako nani?",
            ("Nice to meet you", "en", "sw"): "Nimefurahi kukutana nawe",
            ("Where are you from?", "en", "sw"): "Unatoka wapi?",
            ("See you later", "en", "sw"): "Tutaonana baadaye"
        }
    
    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Mock translation with predefined responses."""
        start_time = time.time()
        
        # Simulate processing delay
        time.sleep(0.1)
        
        # Look for predefined translation
        key = (request.text.strip(), request.source_language.value, request.target_language.value)
        
        if key in self.mock_translations:
            translated_text = self.mock_translations[key]
            confidence = 0.95
        else:
            # Generate mock translation
            if request.target_language == LanguageCode.SWAHILI:
                translated_text = f"[SW] {request.text}"
            else:
                translated_text = f"[{request.target_language.value.upper()}] {request.text}"
            confidence = 0.75
        
        service_time = time.time() - start_time
        
        return TranslationResponse(
            request_id=request.id,
            translated_text=translated_text,
            source_text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            service=self.service_type,
            confidence_score=confidence,
            service_response_time=service_time,
            cost_estimate=0.0,  # Mock service is free
            completed_at=datetime.now()
        )


class OfflineTranslationService(BaseTranslationService):
    """Offline/local translation service using downloaded models."""
    
    def __init__(self, model_path: Optional[str] = None, **kwargs):
        """
        Initialize offline translation service.
        
        Args:
            model_path: Path to local translation model
        """
        super().__init__(TranslationService.OFFLINE_MODEL, **kwargs)
        self.model_path = model_path
        self._model = None
        
        # Try to load model
        self._load_model()
    
    def _load_model(self):
        """Load the offline translation model."""
        try:
            # This would typically load a transformers model or similar
            # For now, we'll use a simple fallback
            logger.info("Offline model would be loaded here")
            self._model = "mock_model"  # Placeholder
        except Exception as e:
            logger.warning(f"Could not load offline model: {e}")
            self._model = None
    
    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate using offline model."""
        start_time = time.time()
        
        if not self._model:
            return TranslationResponse(
                request_id=request.id,
                translated_text="",
                source_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                service=self.service_type,
                error="Offline model not available",
                success=False
            )
        
        # Simulate offline translation
        time.sleep(0.5)  # Simulate processing time
        
        # Simple mock translation
        if request.target_language == LanguageCode.SWAHILI:
            translated_text = f"[OFFLINE SW] {request.text}"
        else:
            translated_text = f"[OFFLINE {request.target_language.value.upper()}] {request.text}"
        
        service_time = time.time() - start_time
        
        return TranslationResponse(
            request_id=request.id,
            translated_text=translated_text,
            source_text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            service=self.service_type,
            confidence_score=0.70,  # Lower confidence for offline models
            service_response_time=service_time,
            cost_estimate=0.0,  # Offline is free after initial setup
            completed_at=datetime.now()
        )


# Service factory
def create_translation_service(service_type: TranslationService, **kwargs) -> BaseTranslationService:
    """
    Factory function to create translation services.
    
    Args:
        service_type: Type of service to create
        **kwargs: Service-specific configuration
        
    Returns:
        Translation service instance
    """
    if service_type == TranslationService.GOOGLE_TRANSLATE:
        return GoogleTranslateService(**kwargs)
    
    elif service_type == TranslationService.OPENAI_GPT:
        api_key = kwargs.get('api_key')
        if not api_key:
            raise TranslationServiceError("OpenAI service requires an API key")
        return OpenAITranslationService(api_key, **kwargs)
    
    elif service_type == TranslationService.OFFLINE_MODEL:
        return OfflineTranslationService(**kwargs)
    
    elif service_type == TranslationService.MOCK:
        return MockTranslationService(**kwargs)
    
    else:
        raise TranslationServiceError(f"Unsupported service type: {service_type}")


# Convenience functions
def translate_text(text: str, 
                  source_lang: LanguageCode = LanguageCode.ENGLISH,
                  target_lang: LanguageCode = LanguageCode.SWAHILI,
                  service_type: TranslationService = TranslationService.MOCK,
                  **kwargs) -> TranslationResponse:
    """
    Convenience function for translating a single text.
    
    Args:
        text: Text to translate
        source_lang: Source language
        target_lang: Target language
        service_type: Translation service to use
        **kwargs: Service configuration
        
    Returns:
        Translation response
    """
    service = create_translation_service(service_type, **kwargs)
    request = TranslationRequest(
        text=text,
        source_language=source_lang,
        target_language=target_lang
    )
    return service.translate(request)
