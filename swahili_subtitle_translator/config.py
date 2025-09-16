"""
Configuration management for Swahili Subtitle Translator.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class TranslationConfig:
    """Configuration for translation services."""
    
    # API Keys
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    
    # Service preferences
    default_service: str = "google_translate"
    fallback_services: list = field(default_factory=lambda: ["offline_model", "mock"])
    
    # Quality settings
    quality_threshold: float = 0.6
    max_retries: int = 3
    
    # Performance settings
    batch_size: int = 100
    parallel_processing: bool = True
    rate_limit: float = 1.0


@dataclass
class SearchConfig:
    """Configuration for subtitle search."""
    
    # Search preferences
    default_sources: list = field(default_factory=lambda: ["opensubtitles", "subscene", "yify"])
    max_results: int = 10
    timeout: int = 30
    
    # Download settings
    download_directory: str = "./downloads"
    overwrite_existing: bool = False
    
    # OpenSubtitles settings
    opensubtitles_api_key: Optional[str] = None
    opensubtitles_user_agent: str = "Swahili Subtitle Translator v1.0.0"


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # General settings
    debug: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Language settings
    default_source_language: str = "en"
    default_target_language: str = "sw"
    
    # UI settings
    show_progress: bool = True
    colored_output: bool = True
    
    # Component configurations
    translation: TranslationConfig = field(default_factory=TranslationConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    
    # File paths
    config_file: Optional[str] = None
    cache_directory: str = "./cache"


class ConfigManager:
    """Manages application configuration with multiple sources."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or self._get_default_config_file()
        self.config = AppConfig()
        
        # Load configuration from various sources
        self._load_configuration()
    
    def _get_default_config_file(self) -> Path:
        """Get default configuration file location."""
        # Try different locations
        possible_locations = [
            Path.cwd() / "swahili_translator_config.json",
            Path.home() / ".config" / "swahili-subtitle-translator" / "config.json",
            Path.home() / ".swahili_translator.json"
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        
        # Return the first preference if none exist
        return possible_locations[0]
    
    def _load_configuration(self):
        """Load configuration from all available sources."""
        # 1. Load from file (if exists)
        if self.config_file.exists():
            try:
                self._load_from_file()
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # 2. Override with environment variables
        self._load_from_environment()
        
        # 3. Set config file path in config
        self.config.config_file = str(self.config_file)
        
        # 4. Create directories if needed
        self._ensure_directories()
    
    def _load_from_file(self):
        """Load configuration from JSON file."""
        with open(self.config_file, 'r') as f:
            data = json.load(f)
        
        # Update configuration fields
        if 'translation' in data:
            for key, value in data['translation'].items():
                if hasattr(self.config.translation, key):
                    setattr(self.config.translation, key, value)
        
        if 'search' in data:
            for key, value in data['search'].items():
                if hasattr(self.config.search, key):
                    setattr(self.config.search, key, value)
        
        # Update main config fields
        for key, value in data.items():
            if key not in ['translation', 'search'] and hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        env_mappings = {
            # Translation service keys
            'GOOGLE_TRANSLATE_API_KEY': ('translation', 'google_api_key'),
            'OPENAI_API_KEY': ('translation', 'openai_api_key'),
            'AZURE_TRANSLATOR_KEY': ('translation', 'azure_api_key'),
            
            # Search settings
            'OPENSUBTITLES_API_KEY': ('search', 'opensubtitles_api_key'),
            'DOWNLOAD_DIR': ('search', 'download_directory'),
            
            # General settings
            'SWAHILI_TRANSLATOR_DEBUG': ('', 'debug'),
            'SWAHILI_TRANSLATOR_VERBOSE': ('', 'verbose'),
            'SWAHILI_TRANSLATOR_LOG_LEVEL': ('', 'log_level'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                if section:
                    # Nested configuration
                    section_obj = getattr(self.config, section)
                    if hasattr(section_obj, key):
                        # Convert boolean strings
                        if key in ['debug', 'verbose', 'parallel_processing', 'overwrite_existing']:
                            value = value.lower() in ('true', '1', 'yes', 'on')
                        # Convert numeric strings
                        elif key in ['quality_threshold', 'rate_limit']:
                            value = float(value)
                        elif key in ['max_retries', 'batch_size', 'max_results', 'timeout']:
                            value = int(value)
                        
                        setattr(section_obj, key, value)
                else:
                    # Main configuration
                    if hasattr(self.config, key):
                        if key in ['debug', 'verbose', 'show_progress', 'colored_output']:
                            value = value.lower() in ('true', '1', 'yes', 'on')
                        setattr(self.config, key, value)
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            self.config.search.download_directory,
            self.config.cache_directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_configuration(self):
        """Save current configuration to file."""
        try:
            config_dict = asdict(self.config)
            
            # Remove non-serializable fields
            config_dict.pop('config_file', None)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_config(self) -> AppConfig:
        """Get current configuration."""
        return self.config
    
    def update_config(self, **kwargs):
        """Update configuration fields."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return issues."""
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check API keys
        if not any([
            self.config.translation.google_api_key,
            self.config.translation.openai_api_key
        ]) and self.config.translation.default_service not in ['mock', 'offline_model']:
            issues['warnings'].append(
                "No API keys configured. Only mock and offline services will be available."
            )
        
        # Check download directory
        download_path = Path(self.config.search.download_directory)
        if not download_path.exists():
            try:
                download_path.mkdir(parents=True, exist_ok=True)
                issues['info'].append(f"Created download directory: {download_path}")
            except Exception as e:
                issues['errors'].append(f"Cannot create download directory: {e}")
        
        # Check quality threshold
        if not 0 <= self.config.translation.quality_threshold <= 1:
            issues['errors'].append("Quality threshold must be between 0 and 1")
        
        # Check log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.config.log_level.upper() not in valid_log_levels:
            issues['warnings'].append(
                f"Invalid log level: {self.config.log_level}. Using INFO."
            )
            self.config.log_level = 'INFO'
        
        return issues
    
    def setup_logging(self):
        """Set up logging based on configuration."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        # Configure root logger
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        if self.config.log_file:
            logging.basicConfig(
                level=log_level,
                format=log_format,
                filename=self.config.log_file,
                filemode='a'
            )
            
            # Also log to console if verbose
            if self.config.verbose:
                console = logging.StreamHandler()
                console.setLevel(log_level)
                formatter = logging.Formatter(log_format)
                console.setFormatter(formatter)
                logging.getLogger('').addHandler(console)
        else:
            logging.basicConfig(
                level=log_level,
                format=log_format
            )
        
        # Set specific logger levels
        if not self.config.debug:
            # Reduce noise from third-party libraries
            logging.getLogger('requests').setLevel(logging.WARNING)
            logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    def print_config_summary(self):
        """Print a summary of current configuration."""
        print("\n🔧 Configuration Summary")
        print("=" * 50)
        
        print(f"Config file: {self.config_file}")
        print(f"Debug mode: {self.config.debug}")
        print(f"Log level: {self.config.log_level}")
        print(f"Languages: {self.config.default_source_language} → {self.config.default_target_language}")
        
        print(f"\nTranslation:")
        print(f"  Default service: {self.config.translation.default_service}")
        print(f"  Quality threshold: {self.config.translation.quality_threshold}")
        print(f"  Google API: {'✓' if self.config.translation.google_api_key else '✗'}")
        print(f"  OpenAI API: {'✓' if self.config.translation.openai_api_key else '✗'}")
        
        print(f"\nSearch:")
        print(f"  Sources: {', '.join(self.config.search.default_sources)}")
        print(f"  Download dir: {self.config.search.download_directory}")
        print(f"  Max results: {self.config.search.max_results}")


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Get current application configuration."""
    return get_config_manager().get_config()


def setup_logging():
    """Set up logging using current configuration."""
    get_config_manager().setup_logging()


# Sample configuration file content
SAMPLE_CONFIG = {
    "debug": False,
    "verbose": False,
    "log_level": "INFO",
    "default_source_language": "en",
    "default_target_language": "sw",
    "show_progress": True,
    "colored_output": True,
    
    "translation": {
        "google_api_key": None,
        "openai_api_key": None,
        "default_service": "google_translate",
        "fallback_services": ["offline_model", "mock"],
        "quality_threshold": 0.6,
        "max_retries": 3,
        "batch_size": 100,
        "parallel_processing": True,
        "rate_limit": 1.0
    },
    
    "search": {
        "default_sources": ["opensubtitles", "subscene", "yify"],
        "max_results": 10,
        "timeout": 30,
        "download_directory": "./downloads",
        "overwrite_existing": False,
        "opensubtitles_api_key": None,
        "opensubtitles_user_agent": "Swahili Subtitle Translator v1.0.0"
    }
}


def create_sample_config(config_path: Path):
    """Create a sample configuration file."""
    with open(config_path, 'w') as f:
        json.dump(SAMPLE_CONFIG, f, indent=2)
    
    print(f"✓ Sample configuration created at: {config_path}")
    print("Edit this file to customize your settings.")
