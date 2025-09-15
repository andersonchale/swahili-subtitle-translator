"""
Translation cache system for improved performance and reduced API calls.
"""

import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from .exceptions import CacheError

logger = logging.getLogger(__name__)


class TranslationCache:
    """
    SQLite-based translation cache for storing and retrieving translations.
    
    Features:
    - Persistent storage using SQLite
    - Automatic cleanup of old entries
    - Hash-based key generation
    - Statistics tracking
    """
    
    def __init__(self, cache_dir: Path, max_age_days: int = 30):
        """
        Initialize translation cache.
        
        Args:
            cache_dir: Directory to store cache database
            max_age_days: Maximum age for cache entries in days
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / "translations.db"
        self.max_age_days = max_age_days
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0,
            'errors': 0
        }
        
        self._init_database()
        
    def _init_database(self):
        """Initialize the SQLite database."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS translations (
                        key TEXT PRIMARY KEY,
                        source_text TEXT NOT NULL,
                        translated_text TEXT NOT NULL,
                        source_lang TEXT NOT NULL,
                        target_lang TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        last_used INTEGER NOT NULL,
                        use_count INTEGER DEFAULT 1
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_created_at ON translations(created_at)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_last_used ON translations(last_used)
                ''')
                
                conn.commit()
                
            logger.debug(f"Cache database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise CacheError(f"Cache initialization failed: {e}")
    
    def _generate_key(self, source_text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key from text and language pair."""
        combined = f"{source_lang}:{target_lang}:{source_text}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[str]:
        """
        Get translation from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Translated text if found, None otherwise
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    'SELECT translated_text, use_count FROM translations WHERE key = ?',
                    (key,)
                )
                result = cursor.fetchone()
                
                if result:
                    translated_text, use_count = result
                    
                    # Update last_used and use_count
                    current_time = int(time.time())
                    conn.execute(
                        'UPDATE translations SET last_used = ?, use_count = ? WHERE key = ?',
                        (current_time, use_count + 1, key)
                    )
                    conn.commit()
                    
                    self.stats['hits'] += 1
                    logger.debug(f"Cache hit for key: {key[:8]}...")
                    return translated_text
                else:
                    self.stats['misses'] += 1
                    logger.debug(f"Cache miss for key: {key[:8]}...")
                    return None
                    
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, translated_text: str, source_text: str = "", 
            source_lang: str = "en", target_lang: str = "sw"):
        """
        Store translation in cache.
        
        Args:
            key: Cache key
            translated_text: Translated text
            source_text: Original source text (for debugging)
            source_lang: Source language code
            target_lang: Target language code
        """
        try:
            current_time = int(time.time())
            
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO translations 
                    (key, source_text, translated_text, source_lang, target_lang, 
                     created_at, last_used, use_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                ''', (key, source_text, translated_text, source_lang, target_lang,
                      current_time, current_time))
                
                conn.commit()
                
            self.stats['saves'] += 1
            logger.debug(f"Cached translation for key: {key[:8]}...")
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache set error: {e}")
    
    def get_by_text(self, source_text: str, source_lang: str = "en", 
                   target_lang: str = "sw") -> Optional[str]:
        """
        Get translation by source text and language pair.
        
        Args:
            source_text: Source text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text if found, None otherwise
        """
        key = self._generate_key(source_text, source_lang, target_lang)
        return self.get(key)
    
    def set_by_text(self, source_text: str, translated_text: str,
                   source_lang: str = "en", target_lang: str = "sw"):
        """
        Store translation by source text and language pair.
        
        Args:
            source_text: Source text
            translated_text: Translated text
            source_lang: Source language code
            target_lang: Target language code
        """
        key = self._generate_key(source_text, source_lang, target_lang)
        self.set(key, translated_text, source_text, source_lang, target_lang)
    
    def cleanup_old_entries(self):
        """Remove entries older than max_age_days."""
        try:
            cutoff_time = int(time.time()) - (self.max_age_days * 24 * 3600)
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    'SELECT COUNT(*) FROM translations WHERE created_at < ?',
                    (cutoff_time,)
                )
                old_count = cursor.fetchone()[0]
                
                if old_count > 0:
                    conn.execute(
                        'DELETE FROM translations WHERE created_at < ?',
                        (cutoff_time,)
                    )
                    conn.commit()
                    
                    logger.info(f"Cleaned up {old_count} old cache entries")
                
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
    
    def clear(self):
        """Clear all cache entries."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute('DELETE FROM translations')
                conn.commit()
                
            logger.info("Cache cleared")
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            raise CacheError(f"Failed to clear cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM translations')
                total_entries = cursor.fetchone()[0]
                
                cursor = conn.execute('''
                    SELECT 
                        AVG(use_count) as avg_use_count,
                        MAX(use_count) as max_use_count,
                        COUNT(CASE WHEN created_at > ? THEN 1 END) as recent_entries
                    FROM translations
                ''', (int(time.time()) - 86400,))  # Last 24 hours
                
                result = cursor.fetchone()
                avg_use, max_use, recent = result
                
            stats = self.stats.copy()
            stats.update({
                'total_entries': total_entries,
                'avg_use_count': round(avg_use or 0, 2),
                'max_use_count': max_use or 0,
                'recent_entries': recent or 0,
                'hit_rate': (
                    stats['hits'] / (stats['hits'] + stats['misses']) 
                    if (stats['hits'] + stats['misses']) > 0 else 0
                ),
                'cache_size_mb': self.get_cache_size_mb()
            })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return self.stats.copy()
    
    def get_cache_size_mb(self) -> float:
        """Get cache database size in MB."""
        try:
            if self.db_path.exists():
                size_bytes = self.db_path.stat().st_size
                return round(size_bytes / (1024 * 1024), 2)
            return 0.0
        except:
            return 0.0
    
    def export_cache(self, export_path: Path):
        """
        Export cache to JSON file.
        
        Args:
            export_path: Path to export file
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM translations')
                rows = cursor.fetchall()
                
            # Convert to list of dictionaries
            data = [dict(row) for row in rows]
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Cache exported to {export_path}")
            
        except Exception as e:
            logger.error(f"Cache export error: {e}")
            raise CacheError(f"Failed to export cache: {e}")
    
    def import_cache(self, import_path: Path):
        """
        Import cache from JSON file.
        
        Args:
            import_path: Path to import file
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            with sqlite3.connect(str(self.db_path)) as conn:
                for entry in data:
                    conn.execute('''
                        INSERT OR REPLACE INTO translations 
                        (key, source_text, translated_text, source_lang, target_lang,
                         created_at, last_used, use_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entry['key'], entry['source_text'], entry['translated_text'],
                        entry['source_lang'], entry['target_lang'],
                        entry['created_at'], entry['last_used'], entry['use_count']
                    ))
                
                conn.commit()
                
            logger.info(f"Cache imported from {import_path}")
            
        except Exception as e:
            logger.error(f"Cache import error: {e}")
            raise CacheError(f"Failed to import cache: {e}")
    
    def save(self):
        """Save cache to disk (SQLite handles this automatically)."""
        # SQLite automatically saves to disk, but we can use this for cleanup
        self.cleanup_old_entries()
    
    def __del__(self):
        """Cleanup when cache object is destroyed."""
        try:
            self.save()
        except:
            pass
