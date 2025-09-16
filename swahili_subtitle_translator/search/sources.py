"""
Subtitle source implementations for various websites and APIs.
"""

import re
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, quote
from pathlib import Path
import tempfile
import zipfile
import io

import requests
from bs4 import BeautifulSoup

from .models import SearchResult, SearchQuery, SourceType, SubtitleFormat
from ..utils.exceptions import SubtitleTranslatorError

logger = logging.getLogger(__name__)


class SubtitleSourceError(SubtitleTranslatorError):
    """Exception raised by subtitle sources."""
    pass


class SubtitleSource(ABC):
    """Abstract base class for subtitle sources."""
    
    def __init__(self, base_url: str, name: str, rate_limit: float = 1.0):
        """
        Initialize subtitle source.
        
        Args:
            base_url: Base URL for the subtitle source
            name: Display name for the source
            rate_limit: Minimum delay between requests (seconds)
        """
        self.base_url = base_url.rstrip('/')
        self.name = name
        self.rate_limit = rate_limit
        self.session = requests.Session()
        # Use more realistic browser headers to avoid 403 errors
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        self._last_request_time = 0
        self._session_initialized = False
    
    def _initialize_session(self):
        """Initialize session by visiting the home page to get cookies."""
        if self._session_initialized:
            return
            
        try:
            logger.debug(f"Initializing session for {self.name}")
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self._session_initialized = True
                logger.debug(f"Session initialized for {self.name}")
        except Exception as e:
            logger.warning(f"Failed to initialize session for {self.name}: {e}")
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, url: str, max_retries: int = 3, **kwargs) -> requests.Response:
        """Make a rate-limited HTTP request with retry logic."""
        self._initialize_session()
        
        for attempt in range(max_retries):
            self._rate_limit_wait()
            
            try:
                # Add some randomization to avoid being detected as a bot
                headers = kwargs.pop('headers', {})
                headers.update({
                    'Referer': self.base_url,
                })
                
                response = self.session.get(url, timeout=30, headers=headers, **kwargs)
                
                if response.status_code == 403:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + (time.time() % 3)  # Exponential backoff with jitter
                        logger.warning(f"Got 403, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Still getting 403 after {max_retries} attempts, giving up")
                        raise SubtitleSourceError(f"Access denied (403) after {max_retries} retries")
                
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + (time.time() % 2)
                    logger.warning(f"Request failed, retrying in {wait_time:.1f}s: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Request to {url} failed after {max_retries} attempts: {e}")
                    raise SubtitleSourceError(f"Request failed: {e}")
    
    @abstractmethod
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Search for subtitles based on query.
        
        Args:
            query: Search parameters
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    def download_subtitle(self, result: SearchResult, output_path: Path) -> Path:
        """
        Download subtitle file.
        
        Args:
            result: Search result to download
            output_path: Path to save the subtitle file
            
        Returns:
            Path to the downloaded file
        """
        pass


class TVSubtitlesSource(SubtitleSource):
    """TVSubtitles.net - Less aggressive anti-bot measures."""
    
    def __init__(self):
        super().__init__(
            base_url="http://www.tvsubtitles.net",
            name="TVSubtitles",
            rate_limit=2.0
        )
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search TVSubtitles for subtitles."""
        logger.info(f"Searching TVSubtitles for: {query.title}")
        
        try:
            search_url = f"{self.base_url}/search.php"
            params = {
                'q': query.title,
                'l': 'en' if query.language == 'en' else query.language
            }
            
            response = self._make_request(search_url, params=params)
            return self._parse_tvsubtitles_results(response.content, query)
            
        except Exception as e:
            logger.error(f"TVSubtitles search failed: {e}")
            return []
    
    def _parse_tvsubtitles_results(self, html_content: bytes, query: SearchQuery) -> List[SearchResult]:
        """Parse TVSubtitles search results."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Look for TV show links
        show_links = soup.find_all('a', href=re.compile(r'/tvshow-\d+\.html'))
        
        for i, link in enumerate(show_links[:query.limit]):
            try:
                title = link.get_text(strip=True)
                show_url = urljoin(self.base_url, link['href'])
                
                result = SearchResult(
                    id=f"tvsubtitles_{i}",
                    title=title,
                    source=SourceType.YIFY,  # Reuse enum value
                    language=query.language or 'en',
                    format=SubtitleFormat.SRT,
                    download_url=show_url,
                    display_name=f"{title} (TVSubtitles)",
                    release_info="TV Show",
                    download_count=0,
                    file_size=None
                )
                results.append(result)
                
            except Exception as e:
                logger.debug(f"Failed to parse TVSubtitles result: {e}")
                continue
        
        logger.info(f"Found {len(results)} TVSubtitles results")
        return results
    
    def download_subtitle(self, result: SearchResult, output_path: Path) -> Path:
        """Download subtitle from TVSubtitles."""
        # This would need to be implemented to navigate to episode pages
        # For now, just create a placeholder
        output_path.write_text("# TVSubtitles download not fully implemented yet\n")
        return output_path

class OpenSubtitlesSource(SubtitleSource):
    """OpenSubtitles.org subtitle source with REST API support."""
    
    def __init__(self, api_key: Optional[str] = None, use_api: bool = False):
        """
        Initialize OpenSubtitles source.
        
        Args:
            api_key: Optional API key for REST API access
            use_api: Whether to use REST API (requires api_key) or web scraping
        """
        if use_api and api_key:
            super().__init__(
                base_url="https://api.opensubtitles.com/api/v1",
                name="OpenSubtitles API",
                rate_limit=0.5  # API has higher rate limits
            )
            self.use_api = True
            self.session.headers.update({
                'Api-Key': api_key,
                'Content-Type': 'application/json'
            })
        else:
            super().__init__(
                base_url="https://www.opensubtitles.org",
                name="OpenSubtitles",
                rate_limit=2.0  # Be more conservative with web scraping
            )
            self.use_api = False
        
        self.api_key = api_key
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search OpenSubtitles for subtitles."""
        logger.info(f"Searching OpenSubtitles for: {query.title}")
        
        try:
            if self.use_api and self.api_key:
                return self._search_api(query)
            else:
                return self._search_web(query)
        except Exception as e:
            logger.error(f"OpenSubtitles search failed: {e}")
            return []
    
    def _search_api(self, query: SearchQuery) -> List[SearchResult]:
        """Search using OpenSubtitles REST API."""
        search_params = {
            'query': query.title,
            'languages': query.language or 'en'
        }
        
        if query.year:
            search_params['year'] = query.year
        
        search_url = f"{self.base_url}/subtitles"
        response = self._make_request(search_url, params=search_params)
        
        data = response.json()
        return self._parse_api_results(data.get('data', []), query)
    
    def _search_web(self, query: SearchQuery) -> List[SearchResult]:
        """Search using web scraping (fallback method)."""
        search_url = self._build_search_url(query)
        response = self._make_request(search_url)
        
        return self._parse_search_results(response.content, query)
    
    def _build_search_url(self, query: SearchQuery) -> str:
        """Build search URL for OpenSubtitles."""
        params = []
        
        # Add title search
        if query.title:
            params.append(f"moviename={quote(query.title)}")
        
        # Add language filter
        if query.language:
            params.append(f"sublanguageid={query.language}")
        
        # Add season/episode if TV show
        if query.season is not None:
            params.append(f"season={query.season}")
        if query.episode is not None:
            params.append(f"episode={query.episode}")
        
        query_string = "&".join(params)
        return f"{self.base_url}/en/search/sublanguageid-{query.language}/moviename-{quote(query.title)}"
    
    def _parse_search_results(self, html_content: bytes, query: SearchQuery) -> List[SearchResult]:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Look for subtitle entries in the results table
        subtitle_rows = soup.find_all('tr', {'id': re.compile(r'name\d+')})
        
        for i, row in enumerate(subtitle_rows[:query.limit]):
            try:
                result = self._parse_subtitle_row(row, i)
                if result:
                    results.append(result)
            except Exception as e:
                logger.debug(f"Failed to parse subtitle row: {e}")
                continue
        
        logger.info(f"Found {len(results)} OpenSubtitles results")
        return results
    
    def _parse_subtitle_row(self, row, index: int) -> Optional[SearchResult]:
        """Parse a single subtitle row."""
        try:
            # Extract basic information
            title_link = row.find('a', {'href': re.compile(r'/en/subtitles/')})
            if not title_link:
                return None
            
            title = title_link.get_text(strip=True)
            download_link = row.find('a', {'href': re.compile(r'/en/subtitleserve/')})
            
            if not download_link:
                return None
            
            download_url = urljoin(self.base_url, download_link['href'])
            
            # Extract additional metadata
            release_info = None
            release_cell = row.find('td', class_='MovieRelease')
            if release_cell:
                release_info = release_cell.get_text(strip=True)
            
            # Create search result
            return SearchResult(
                id=f"opensubtitles_{index}",
                title=title,
                year=None,  # Could be parsed from title if needed
                language="en",  # Default, could be extracted
                format=SubtitleFormat.SRT,  # Default format
                source=SourceType.OPENSUBTITLES,
                download_url=download_url,
                release_info=release_info
            )
            
        except Exception as e:
            logger.debug(f"Failed to parse subtitle row: {e}")
            return None
    
    def download_subtitle(self, result: SearchResult, output_path: Path) -> Path:
        """Download subtitle from OpenSubtitles."""
        logger.info(f"Downloading subtitle: {result.display_name}")
        
        try:
            response = self._make_request(result.download_url)
            
            # Handle different content types
            if response.headers.get('content-type', '').startswith('application/zip'):
                # Extract from ZIP file
                return self._extract_from_zip(response.content, output_path)
            else:
                # Direct subtitle file
                output_path.write_bytes(response.content)
                return output_path
                
        except Exception as e:
            raise SubtitleSourceError(f"Download failed: {e}")
    
    def _extract_from_zip(self, zip_content: bytes, output_path: Path) -> Path:
        """Extract subtitle from ZIP archive."""
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
            # Find subtitle files
            subtitle_files = [f for f in zf.namelist() 
                            if f.lower().endswith(('.srt', '.ass', '.ssa', '.vtt', '.sub'))]
            
            if not subtitle_files:
                raise SubtitleSourceError("No subtitle files found in archive")
            
            # Extract the first subtitle file
            subtitle_file = subtitle_files[0]
            content = zf.read(subtitle_file)
            
            # Adjust output path extension if needed
            original_ext = Path(subtitle_file).suffix
            if output_path.suffix != original_ext:
                output_path = output_path.with_suffix(original_ext)
            
            output_path.write_bytes(content)
        return output_path


class SubsceneSource(SubtitleSource):
    """Subscene.com subtitle source."""
    
    def __init__(self):
        super().__init__(
            base_url="https://subscene.com",
            name="Subscene",
            rate_limit=2.0
        )
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search Subscene for subtitles."""
        logger.info(f"Searching Subscene for: {query.title}")
        
        try:
            search_url = f"{self.base_url}/subtitles/searchbytitle"
            data = {
                'query': query.title,
                'l': ''
            }
            
            # Subscene uses POST for search
            response = self.session.post(search_url, data=data, timeout=30)
            response.raise_for_status()
            
            return self._parse_subscene_results(response.content, query)
            
        except Exception as e:
            logger.error(f"Subscene search failed: {e}")
            return []
    
    def _parse_subscene_results(self, html_content: bytes, query: SearchQuery) -> List[SearchResult]:
        """Parse Subscene search results."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Look for movie/TV show results
        title_links = soup.find_all('a', href=re.compile(r'/subtitles/'))
        
        for i, link in enumerate(title_links[:query.limit]):
            try:
                title = link.get_text(strip=True)
                detail_url = urljoin(self.base_url, link['href'])
                
                result = SearchResult(
                    id=f"subscene_{i}",
                    title=title,
                    year=None,
                    source=SourceType.SUBSCENE,
                    language=query.language or 'en',
                    format=SubtitleFormat.SRT,
                    download_url=detail_url,
                    release_info="Subscene",
                    download_count=None,
                    file_size=None
                )
                results.append(result)
                
            except Exception as e:
                logger.debug(f"Failed to parse Subscene result: {e}")
                continue
        
        logger.info(f"Found {len(results)} Subscene results")
        return results
    
    def download_subtitle(self, result: SearchResult, output_path: Path) -> Path:
        """Download subtitle from Subscene."""
        # This would need to be implemented to navigate to subtitle pages
        # For now, just create a placeholder
        output_path.write_text("# Subscene download not fully implemented yet\n")
        return output_path


class MockSubtitleSource(SubtitleSource):
    """Mock subtitle source for testing and demonstration."""
    
    def __init__(self):
        super().__init__(
            base_url="https://example.com",
            name="Mock Subtitle Source",
            rate_limit=0.5
        )
        
        # Sample mock data
        self.mock_results = {
            "matrix": [
                {
                    "title": "The Matrix (1999)",
                    "release_info": "BluRay.1080p.x264",
                    "language": "en",
                    "download_url": "https://example.com/download/matrix_1999.srt"
                },
                {
                    "title": "The Matrix Reloaded (2003)", 
                    "release_info": "DVDRip.XviD",
                    "language": "en",
                    "download_url": "https://example.com/download/matrix_reloaded.srt"
                }
            ],
            "avatar": [
                {
                    "title": "Avatar (2009)",
                    "release_info": "BluRay.1080p.x264-SECTOR7",
                    "language": "en",
                    "download_url": "https://example.com/download/avatar_2009.srt"
                }
            ],
            "inception": [
                {
                    "title": "Inception (2010)",
                    "release_info": "BluRay.720p.x264",
                    "language": "en", 
                    "download_url": "https://example.com/download/inception.srt"
                }
            ]
        }
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Mock search that returns sample results."""
        logger.info(f"Mock searching for: {query.title}")
        
        # Simple keyword matching
        query_lower = query.title.lower()
        found_results = []
        
        for keyword, results in self.mock_results.items():
            if keyword in query_lower:
                for i, result_data in enumerate(results[:query.limit]):
                    result = SearchResult(
                        id=f"mock_{keyword}_{i}",
                        title=result_data["title"],
                        year=2009 + i,  # Add year
                        source=SourceType.MOCK,
                        language=result_data["language"],
                        format=SubtitleFormat.SRT,
                        download_url=result_data["download_url"],
                        release_info=result_data["release_info"],
                        download_count=1000 + i * 100,
                        file_size=50000 + i * 5000
                    )
                    found_results.append(result)
        
        # Add some generic results if no specific matches
        if not found_results:
            for i in range(min(3, query.limit)):
                result = SearchResult(
                    id=f"mock_generic_{i}",
                    title=f"{query.title} - Sample Result {i+1}",
                    year=2020 + i,
                    source=SourceType.MOCK,
                    language=query.language or "en",
                    format=SubtitleFormat.SRT,
                    download_url=f"https://example.com/download/sample_{i}.srt",
                    release_info="Sample.Release",
                    download_count=500 + i * 50,
                    file_size=45000 + i * 3000
                )
                found_results.append(result)
        
        logger.info(f"Found {len(found_results)} mock results")
        return found_results
    
    def download_subtitle(self, result: SearchResult, output_path: Path) -> Path:
        """Create a sample subtitle file."""
        sample_content = f"""1
00:00:01,000 --> 00:00:04,000
Sample subtitle for {result.title}

2
00:00:05,000 --> 00:00:08,000
This is a mock subtitle file

3
00:00:09,000 --> 00:00:12,000
Generated for demonstration purposes"""
        
        output_path.write_text(sample_content, encoding='utf-8')
        logger.info(f"Created mock subtitle file: {output_path}")
        return output_path


class OpenSubtitlesSource(SubtitleSource):
    """Subscene.com subtitle source."""
    
    def __init__(self):
        super().__init__(
            base_url="https://subscene.com",
            name="Subscene",
            rate_limit=2.0  # More conservative rate limiting
        )
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search Subscene for subtitles."""
        logger.info(f"Searching Subscene for: {query.title}")
        
        try:
            search_url = f"{self.base_url}/subtitles/searchbytitle"
            data = {'query': query.title}
            
            # Make POST request for search
            self._rate_limit_wait()
            response = self.session.post(search_url, data=data, timeout=30)
            response.raise_for_status()
            
            return self._parse_search_results(response.content, query)
            
        except Exception as e:
            logger.error(f"Subscene search failed: {e}")
            return []
    
    def _parse_search_results(self, html_content: bytes, query: SearchQuery) -> List[SearchResult]:
        """Parse Subscene search results."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Find movie/TV show links
        title_links = soup.find_all('a', {'href': re.compile(r'/subtitles/')})
        
        for i, link in enumerate(title_links[:query.limit]):
            try:
                title = link.get_text(strip=True)
                detail_url = urljoin(self.base_url, link['href'])
                
                result = SearchResult(
                    id=f"subscene_{i}",
                    title=title,
                    year=None,
                    language="en",
                    format=SubtitleFormat.SRT,
                    source=SourceType.SUBSCENE,
                    download_url=detail_url  # This is actually a detail page
                )
                results.append(result)
                
            except Exception as e:
                logger.debug(f"Failed to parse Subscene result: {e}")
                continue
        
        logger.info(f"Found {len(results)} Subscene results")
        return results
    
    def download_subtitle(self, result: SearchResult, output_path: Path) -> Path:
        """Download subtitle from Subscene."""
        logger.info(f"Downloading subtitle: {result.display_name}")
        
        try:
            # First get the subtitle detail page
            response = self._make_request(result.download_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find download link
            download_link = soup.find('a', {'href': re.compile(r'/subtitle/download')})
            if not download_link:
                raise SubtitleSourceError("Download link not found")
            
            download_url = urljoin(self.base_url, download_link['href'])
            
            # Download the subtitle
            response = self._make_request(download_url)
            
            # Handle ZIP files
            if response.headers.get('content-type', '').startswith('application/zip'):
                return self._extract_from_zip(response.content, output_path)
            else:
                output_path.write_bytes(response.content)
                return output_path
                
        except Exception as e:
            raise SubtitleSourceError(f"Subscene download failed: {e}")
    
    def _extract_from_zip(self, zip_content: bytes, output_path: Path) -> Path:
        """Extract subtitle from ZIP (same as OpenSubtitles)."""
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
            subtitle_files = [f for f in zf.namelist() 
                            if f.lower().endswith(('.srt', '.ass', '.ssa', '.vtt', '.sub'))]
            
            if not subtitle_files:
                raise SubtitleSourceError("No subtitle files found in archive")
            
            subtitle_file = subtitle_files[0]
            content = zf.read(subtitle_file)
            
            original_ext = Path(subtitle_file).suffix
            if output_path.suffix != original_ext:
                output_path = output_path.with_suffix(original_ext)
            
            output_path.write_bytes(content)
            return output_path


class YIFYSubtitlesSource(SubtitleSource):
    """YIFY Subtitles source."""
    
    def __init__(self):
        super().__init__(
            base_url="https://yifysubtitles.org",
            name="YIFY Subtitles",
            rate_limit=1.5
        )
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search YIFY Subtitles."""
        logger.info(f"Searching YIFY Subtitles for: {query.title}")
        
        try:
            # Build search URL
            search_url = f"{self.base_url}/search"
            params = {'q': query.title}
            
            response = self._make_request(search_url, params=params)
            return self._parse_search_results(response.content, query)
            
        except Exception as e:
            logger.error(f"YIFY search failed: {e}")
            return []
    
    def _parse_search_results(self, html_content: bytes, query: SearchQuery) -> List[SearchResult]:
        """Parse YIFY search results."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Find movie cards or links
        movie_links = soup.find_all('a', {'href': re.compile(r'/movie-imdb/')})
        
        for i, link in enumerate(movie_links[:query.limit]):
            try:
                title = link.get_text(strip=True)
                detail_url = urljoin(self.base_url, link['href'])
                
                result = SearchResult(
                    id=f"yify_{i}",
                    title=title,
                    year=None,
                    language="en",
                    format=SubtitleFormat.SRT,
                    source=SourceType.YIFY,
                    download_url=detail_url
                )
                results.append(result)
                
            except Exception as e:
                logger.debug(f"Failed to parse YIFY result: {e}")
                continue
        
        logger.info(f"Found {len(results)} YIFY results")
        return results
    
    def download_subtitle(self, result: SearchResult, output_path: Path) -> Path:
        """Download subtitle from YIFY."""
        logger.info(f"Downloading subtitle: {result.display_name}")
        
        try:
            # Get movie detail page
            response = self._make_request(result.download_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find subtitle download links
            download_links = soup.find_all('a', {'href': re.compile(r'/subtitle/')})
            if not download_links:
                raise SubtitleSourceError("No subtitle download links found")
            
            # Use first available subtitle
            download_url = urljoin(self.base_url, download_links[0]['href'])
            response = self._make_request(download_url)
            
            # Handle ZIP files
            if response.headers.get('content-type', '').startswith('application/zip'):
                return self._extract_from_zip(response.content, output_path)
            else:
                output_path.write_bytes(response.content)
                return output_path
                
        except Exception as e:
            raise SubtitleSourceError(f"YIFY download failed: {e}")
    
    def _extract_from_zip(self, zip_content: bytes, output_path: Path) -> Path:
        """Extract subtitle from ZIP (same implementation)."""
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
            subtitle_files = [f for f in zf.namelist() 
                            if f.lower().endswith(('.srt', '.ass', '.ssa', '.vtt', '.sub'))]
            
            if not subtitle_files:
                raise SubtitleSourceError("No subtitle files found in archive")
            
            subtitle_file = subtitle_files[0]
            content = zf.read(subtitle_file)
            
            original_ext = Path(subtitle_file).suffix
            if output_path.suffix != original_ext:
                output_path = output_path.with_suffix(original_ext)
            
            output_path.write_bytes(content)
            return output_path
