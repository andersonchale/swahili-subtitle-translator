"""
Main subtitle search engine that coordinates multiple sources.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile

from .models import SearchQuery, SearchResult, SourceType
from .sources import (
    SubtitleSource, 
    OpenSubtitlesSource, 
    SubsceneSource, 
    YIFYSubtitlesSource,
    MockSubtitleSource,
    SubtitleSourceError
)
from ..utils.exceptions import SubtitleTranslatorError

logger = logging.getLogger(__name__)


class SubtitleSearchEngine:
    """Main search engine for coordinating subtitle sources."""
    
    def __init__(self, 
                 opensubtitles_api_key: Optional[str] = None,
                 max_workers: int = 3,
                 timeout_per_source: int = 30):
        """
        Initialize the search engine.
        
        Args:
            opensubtitles_api_key: Optional API key for OpenSubtitles
            max_workers: Maximum number of concurrent source searches
            timeout_per_source: Timeout for each source search in seconds
        """
        self.max_workers = max_workers
        self.timeout_per_source = timeout_per_source
        
        # Initialize sources
        self.sources: Dict[SourceType, SubtitleSource] = {}
        self._initialize_sources(opensubtitles_api_key)
        
        logger.info(f"Initialized search engine with {len(self.sources)} sources")
    
    def _initialize_sources(self, opensubtitles_api_key: Optional[str] = None):
        """Initialize all available subtitle sources."""
        try:
            # Use API if key is provided, otherwise fallback to web scraping
            use_api = bool(opensubtitles_api_key)
            self.sources[SourceType.OPENSUBTITLES] = OpenSubtitlesSource(
                api_key=opensubtitles_api_key, 
                use_api=use_api
            )
            logger.info(f"OpenSubtitles source initialized (API: {use_api})")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenSubtitles source: {e}")
        
        try:
            self.sources[SourceType.SUBSCENE] = SubsceneSource()
            logger.info("Subscene source initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Subscene source: {e}")
        
        try:
            self.sources[SourceType.YIFY] = YIFYSubtitlesSource()
            logger.info("YIFY source initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize YIFY source: {e}")
        
        # Always add mock source for demonstration
        try:
            self.sources[SourceType.MOCK] = MockSubtitleSource()
            logger.info("Mock source initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Mock source: {e}")
    
    def search(self, 
               query: Union[SearchQuery, str], 
               sources: Optional[List[SourceType]] = None,
               parallel: bool = True) -> List[SearchResult]:
        """
        Search for subtitles across multiple sources.
        
        Args:
            query: Search query (can be SearchQuery object or title string)
            sources: List of sources to search (None for all available)
            parallel: Whether to search sources in parallel
            
        Returns:
            Combined list of search results from all sources
        """
        # Convert string to SearchQuery if needed
        if isinstance(query, str):
            query = SearchQuery(title=query)
        
        # Use all sources if none specified
        if sources is None:
            sources = list(self.sources.keys())
        
        # Filter available sources
        available_sources = {
            source_type: source for source_type, source in self.sources.items()
            if source_type in sources
        }
        
        if not available_sources:
            logger.warning("No available sources for search")
            return []
        
        logger.info(f"Searching {len(available_sources)} sources for: {query.title}")
        
        if parallel and len(available_sources) > 1:
            return self._search_parallel(query, available_sources)
        else:
            return self._search_sequential(query, available_sources)
    
    def _search_parallel(self, 
                        query: SearchQuery, 
                        sources: Dict[SourceType, SubtitleSource]) -> List[SearchResult]:
        """Search sources in parallel using ThreadPoolExecutor."""
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit search tasks
            future_to_source = {
                executor.submit(self._search_single_source, source, query): source_type
                for source_type, source in sources.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_source, timeout=self.timeout_per_source):
                source_type = future_to_source[future]
                try:
                    results = future.result(timeout=5)  # Short timeout for result retrieval
                    all_results.extend(results)
                    logger.info(f"{source_type.value} returned {len(results)} results")
                except Exception as e:
                    logger.error(f"Search failed for {source_type.value}: {e}")
        
        return self._deduplicate_and_sort(all_results)
    
    def _search_sequential(self, 
                          query: SearchQuery, 
                          sources: Dict[SourceType, SubtitleSource]) -> List[SearchResult]:
        """Search sources sequentially."""
        all_results = []
        
        for source_type, source in sources.items():
            try:
                results = self._search_single_source(source, query)
                all_results.extend(results)
                logger.info(f"{source_type.value} returned {len(results)} results")
            except Exception as e:
                logger.error(f"Search failed for {source_type.value}: {e}")
        
        return self._deduplicate_and_sort(all_results)
    
    def _search_single_source(self, source: SubtitleSource, query: SearchQuery) -> List[SearchResult]:
        """Search a single source with error handling."""
        try:
            return source.search(query)
        except SubtitleSourceError as e:
            logger.error(f"Source {source.name} search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching {source.name}: {e}")
            return []
    
    def _deduplicate_and_sort(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicates and sort results by relevance."""
        # Simple deduplication by title and source
        seen = set()
        unique_results = []
        
        for result in results:
            key = (result.title.lower(), result.source)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Sort by source priority and title
        source_priority = {
            SourceType.OPENSUBTITLES: 1,
            SourceType.SUBSCENE: 2,
            SourceType.YIFY: 3,
            SourceType.MOCK: 4  # Mock source has lowest priority
        }
        
        unique_results.sort(key=lambda r: (source_priority.get(r.source, 999), r.title.lower()))
        
        logger.info(f"Returning {len(unique_results)} unique results after deduplication")
        return unique_results
    
    def download_subtitle(self, 
                         result: SearchResult, 
                         output_path: Optional[Path] = None) -> Path:
        """
        Download a subtitle file.
        
        Args:
            result: Search result to download
            output_path: Optional output path (temporary file if not provided)
            
        Returns:
            Path to the downloaded subtitle file
        """
        # Get the appropriate source
        source = self.sources.get(result.source)
        if not source:
            raise SubtitleTranslatorError(f"Source {result.source} not available")
        
        # Generate output path if not provided
        if output_path is None:
            suffix = f".{result.format.value}" if result.format else ".srt"
            output_path = Path(tempfile.mktemp(suffix=suffix))
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading subtitle from {source.name}: {result.display_name}")
        
        try:
            downloaded_path = source.download_subtitle(result, output_path)
            logger.info(f"Successfully downloaded subtitle to: {downloaded_path}")
            return downloaded_path
            
        except SubtitleSourceError as e:
            logger.error(f"Download failed from {source.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected download error from {source.name}: {e}")
            raise SubtitleTranslatorError(f"Download failed: {e}")
    
    def get_available_sources(self) -> List[SourceType]:
        """Get list of available subtitle sources."""
        return list(self.sources.keys())
    
    def get_source_info(self) -> Dict[SourceType, Dict[str, str]]:
        """Get information about available sources."""
        return {
            source_type: {
                'name': source.name,
                'base_url': source.base_url,
                'rate_limit': str(source.rate_limit)
            }
            for source_type, source in self.sources.items()
        }
    
    def test_sources(self, test_query: str = "The Matrix") -> Dict[SourceType, bool]:
        """
        Test all sources with a simple query.
        
        Args:
            test_query: Query to test sources with
            
        Returns:
            Dictionary mapping source types to success status
        """
        logger.info(f"Testing sources with query: {test_query}")
        test_results = {}
        
        query = SearchQuery(title=test_query, limit=3)
        
        for source_type, source in self.sources.items():
            try:
                results = self._search_single_source(source, query)
                test_results[source_type] = len(results) > 0
                logger.info(f"{source.name}: {'✓' if test_results[source_type] else '✗'}")
            except Exception as e:
                test_results[source_type] = False
                logger.error(f"{source.name}: ✗ ({e})")
        
        return test_results


# Convenience function for simple searches
def search_subtitles(title: str, 
                    language: str = "en",
                    limit: int = 10,
                    sources: Optional[List[SourceType]] = None,
                    opensubtitles_api_key: Optional[str] = None) -> List[SearchResult]:
    """
    Convenience function for searching subtitles.
    
    Args:
        title: Movie or TV show title to search for
        language: Subtitle language code (default: "en")
        limit: Maximum number of results per source
        sources: List of sources to search (None for all)
        opensubtitles_api_key: Optional OpenSubtitles API key
        
    Returns:
        List of search results
    """
    engine = SubtitleSearchEngine(opensubtitles_api_key=opensubtitles_api_key)
    query = SearchQuery(title=title, language=language, limit=limit)
    return engine.search(query, sources=sources)
