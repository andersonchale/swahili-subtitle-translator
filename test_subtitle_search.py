#!/usr/bin/env python3
"""
Test script for subtitle search functionality.
"""

import sys
import logging
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from swahili_subtitle_translator.search.engine import SubtitleSearchEngine, search_subtitles
from swahili_subtitle_translator.search.models import SearchQuery, SourceType

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_search_engine_initialization():
    """Test that the search engine initializes properly."""
    print("\n" + "="*60)
    print("Testing Search Engine Initialization")
    print("="*60)
    
    try:
        engine = SubtitleSearchEngine()
        available_sources = engine.get_available_sources()
        
        print(f"✓ Search engine initialized successfully")
        print(f"✓ Available sources: {[source.value for source in available_sources]}")
        
        # Get source info
        source_info = engine.get_source_info()
        for source_type, info in source_info.items():
            print(f"  - {info['name']}: {info['base_url']} (rate limit: {info['rate_limit']}s)")
        
        return engine
        
    except Exception as e:
        print(f"✗ Failed to initialize search engine: {e}")
        return None


def test_source_availability(engine):
    """Test source availability without making actual requests."""
    print("\n" + "="*60)
    print("Testing Source Availability")
    print("="*60)
    
    try:
        # Test with a simple, well-known movie
        test_results = engine.test_sources("The Matrix")
        
        for source_type, success in test_results.items():
            status = "✓" if success else "✗"
            print(f"{status} {source_type.value}: {'Working' if success else 'Not working'}")
        
        working_sources = sum(test_results.values())
        print(f"\nSummary: {working_sources}/{len(test_results)} sources working")
        
        return working_sources > 0
        
    except Exception as e:
        print(f"✗ Source testing failed: {e}")
        return False


def test_simple_search():
    """Test simple subtitle search using convenience function."""
    print("\n" + "="*60)
    print("Testing Simple Search Function")
    print("="*60)
    
    try:
        # Search for a popular movie
        test_title = "Avatar"
        print(f"Searching for subtitles: '{test_title}'")
        
        results = search_subtitles(
            title=test_title,
            language="en",
            limit=3  # Limit results to avoid too much output
        )
        
        print(f"✓ Found {len(results)} subtitle results")
        
        # Display first few results
        for i, result in enumerate(results[:5], 1):
            print(f"  {i}. {result.display_name}")
            print(f"     Source: {result.source.value}")
            if result.release_info:
                print(f"     Release: {result.release_info}")
            print()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"✗ Simple search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detailed_search(engine):
    """Test detailed search with SearchQuery object."""
    print("\n" + "="*60)
    print("Testing Detailed Search")
    print("="*60)
    
    try:
        # Create detailed search query
        query = SearchQuery(
            title="Inception",
            language="en",
            year=2010,
            limit=5
        )
        
        print(f"Searching with detailed query:")
        print(f"  Title: {query.title}")
        print(f"  Language: {query.language}")
        print(f"  Year: {query.year}")
        print(f"  Limit: {query.limit}")
        
        # Search with specific sources
        results = engine.search(
            query=query,
            sources=[SourceType.OPENSUBTITLES, SourceType.SUBSCENE],
            parallel=True
        )
        
        print(f"✓ Found {len(results)} results from specified sources")
        
        # Group by source
        by_source = {}
        for result in results:
            source = result.source.value
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)
        
        for source, source_results in by_source.items():
            print(f"\n{source} ({len(source_results)} results):")
            for result in source_results[:3]:  # Show first 3
                print(f"  - {result.title}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"✗ Detailed search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_download_simulation(engine):
    """Test download simulation (without actually downloading)."""
    print("\n" + "="*60)
    print("Testing Download Simulation")
    print("="*60)
    
    try:
        # First search for something to download
        results = search_subtitles("Shrek", limit=1)
        
        if not results:
            print("⚠ No results found for download test")
            return True  # Not a failure, just no results
        
        result = results[0]
        print(f"Would download: {result.display_name}")
        print(f"Source: {result.source.value}")
        print(f"Download URL: {result.download_url}")
        
        # Create a temporary path for download
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        output_path = temp_dir / "test_subtitle.srt"
        
        print(f"Simulated download path: {output_path}")
        print("✓ Download simulation completed (no actual download performed)")
        
        # Clean up
        temp_dir.rmdir()
        
        return True
        
    except Exception as e:
        print(f"✗ Download simulation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Swahili Subtitle Translator - Search Engine Tests")
    print("="*60)
    
    test_results = []
    
    # Test 1: Engine initialization
    engine = test_search_engine_initialization()
    test_results.append(("Engine Initialization", engine is not None))
    
    if engine is None:
        print("\n❌ Cannot proceed with other tests - engine initialization failed")
        return False
    
    # Test 2: Source availability
    sources_working = test_source_availability(engine)
    test_results.append(("Source Availability", sources_working))
    
    # Test 3: Simple search
    simple_search_ok = test_simple_search()
    test_results.append(("Simple Search", simple_search_ok))
    
    # Test 4: Detailed search
    detailed_search_ok = test_detailed_search(engine)
    test_results.append(("Detailed Search", detailed_search_ok))
    
    # Test 5: Download simulation
    download_ok = test_download_simulation(engine)
    test_results.append(("Download Simulation", download_ok))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The subtitle search system is working correctly.")
        return True
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
