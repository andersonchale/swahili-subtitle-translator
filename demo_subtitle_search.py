#!/usr/bin/env python3
"""
Demo script showing subtitle search functionality with mock data.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from swahili_subtitle_translator.search.models import (
    SearchResult, SearchQuery, SourceType, SubtitleFormat
)
from swahili_subtitle_translator.search.engine import SubtitleSearchEngine


class MockSubtitleSource:
    """Mock subtitle source for demonstration."""
    
    def __init__(self, name: str, source_type: SourceType):
        self.name = name
        self.base_url = f"https://{name.lower().replace(' ', '')}.com"
        self.rate_limit = 1.0
        self.source_type = source_type
    
    def search(self, query: SearchQuery):
        """Return mock search results."""
        results = []
        
        # Generate some mock results based on the query
        if "avatar" in query.title.lower():
            results.extend([
                SearchResult(
                    id=f"{self.source_type.value}_avatar_1",
                    title="Avatar",
                    year=2009,
                    language=query.language,
                    format=SubtitleFormat.SRT,
                    source=self.source_type,
                    download_url=f"{self.base_url}/download/avatar_2009.srt",
                    release_info="BluRay.1080p.x264-YIFY",
                    rating=4.5,
                    download_count=15420
                ),
                SearchResult(
                    id=f"{self.source_type.value}_avatar_2",
                    title="Avatar",
                    year=2009,
                    language=query.language,
                    format=SubtitleFormat.SRT,
                    source=self.source_type,
                    download_url=f"{self.base_url}/download/avatar_dvdrip.srt",
                    release_info="DVDRip.XviD-MAXSPEED",
                    rating=4.2,
                    download_count=8930
                )
            ])
        
        elif "matrix" in query.title.lower():
            results.extend([
                SearchResult(
                    id=f"{self.source_type.value}_matrix_1",
                    title="The Matrix",
                    year=1999,
                    language=query.language,
                    format=SubtitleFormat.SRT,
                    source=self.source_type,
                    download_url=f"{self.base_url}/download/matrix_1999.srt",
                    release_info="BluRay.720p.x264-SiNNERS",
                    rating=4.8,
                    download_count=25830
                )
            ])
        
        elif "inception" in query.title.lower():
            results.extend([
                SearchResult(
                    id=f"{self.source_type.value}_inception_1",
                    title="Inception",
                    year=2010,
                    language=query.language,
                    format=SubtitleFormat.SRT,
                    source=self.source_type,
                    download_url=f"{self.base_url}/download/inception_2010.srt",
                    release_info="BluRay.1080p.DTS.x264-DXVA",
                    rating=4.7,
                    download_count=18750
                )
            ])
        
        # Limit results
        return results[:query.limit]


def demo_search_functionality():
    """Demonstrate the subtitle search functionality with mock data."""
    print("🎬 Swahili Subtitle Translator - Search Demo")
    print("=" * 60)
    print("Note: This demo uses mock data to show functionality")
    print("In real usage, this would connect to actual subtitle websites")
    print("=" * 60)
    
    # Create a custom search engine with mock sources
    engine = SubtitleSearchEngine()
    
    # Replace real sources with mock sources for demo
    engine.sources = {
        SourceType.OPENSUBTITLES: MockSubtitleSource("OpenSubtitles", SourceType.OPENSUBTITLES),
        SourceType.SUBSCENE: MockSubtitleSource("Subscene", SourceType.SUBSCENE),
        SourceType.YIFY: MockSubtitleSource("YIFY Subtitles", SourceType.YIFY)
    }
    
    # Demo 1: Simple search
    print("\n📺 Demo 1: Simple Movie Search")
    print("-" * 40)
    
    results = engine.search("Avatar")
    print(f"Search: 'Avatar' - Found {len(results)} results")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.display_name}")
        print(f"     Source: {result.source.value}")
        print(f"     Release: {result.release_info}")
        print(f"     Rating: {result.rating}/5.0 ({result.download_count:,} downloads)")
        print(f"     URL: {result.download_url}")
        print()
    
    # Demo 2: Detailed search with query object
    print("🔍 Demo 2: Detailed Search with Query Object")
    print("-" * 40)
    
    query = SearchQuery(
        title="The Matrix",
        year=1999,
        language="en",
        limit=5
    )
    
    results = engine.search(query, sources=[SourceType.OPENSUBTITLES, SourceType.SUBSCENE])
    print(f"Search: Detailed query for The Matrix (1999)")
    print(f"Sources: OpenSubtitles, Subscene")
    print(f"Found {len(results)} results")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.display_name}")
        print(f"     Source: {result.source.value}")
        print(f"     Release: {result.release_info}")
        print(f"     Rating: {result.rating}/5.0")
        print()
    
    # Demo 3: Source information
    print("ℹ️  Demo 3: Available Sources Information")
    print("-" * 40)
    
    source_info = engine.get_source_info()
    for source_type, info in source_info.items():
        print(f"  {info['name']}")
        print(f"    URL: {info['base_url']}")
        print(f"    Rate limit: {info['rate_limit']}s between requests")
        print()
    
    # Demo 4: Show data model features
    print("📊 Demo 4: Data Model Features")
    print("-" * 40)
    
    # Create a sample result
    sample_result = SearchResult(
        id="demo_result",
        title="Inception",
        year=2010,
        language="en",
        format=SubtitleFormat.SRT,
        source=SourceType.OPENSUBTITLES,
        download_url="https://example.com/inception.srt",
        release_info="BluRay.1080p.x264",
        rating=4.7,
        download_count=18750,
        hearing_impaired=False
    )
    
    print("Sample SearchResult object:")
    print(f"  Display Name: {sample_result.display_name}")
    print(f"  Is TV Show: {sample_result.is_tv_show}")
    print(f"  JSON Export: Available via .to_dict()")
    
    # Show dictionary representation
    result_dict = sample_result.to_dict()
    print("\nJSON-serializable format:")
    for key, value in list(result_dict.items())[:8]:  # Show first 8 fields
        print(f"  {key}: {value}")
    print("  ... (and more)")
    
    print("\n🎉 Demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("  ✅ Multi-source subtitle search")
    print("  ✅ Flexible search queries")
    print("  ✅ Rich metadata extraction") 
    print("  ✅ Structured data models")
    print("  ✅ JSON serialization support")
    print("  ✅ Rate limiting and error handling")
    
    print(f"\n📁 Project Structure:")
    print("  swahili_subtitle_translator/")
    print("    search/")
    print("      ├── engine.py      # Main search coordination")
    print("      ├── sources.py     # Subtitle source implementations")
    print("      ├── models.py      # Data models and types")
    print("      └── __init__.py    # Public API exports")
    
    return True


if __name__ == "__main__":
    try:
        demo_search_functionality()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
