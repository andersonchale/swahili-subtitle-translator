#!/usr/bin/env python3
"""
Basic test script to verify the new subtitle translator works.
"""

import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from swahili_subtitle_translator.core.translator import SubtitleTranslator
from swahili_subtitle_translator.core.processor import SubtitleProcessor

def test_basic_translation():
    """Test basic translation functionality."""
    print("🧪 Testing basic translation...")
    
    # Create translator (disable cache for testing)
    translator = SubtitleTranslator(enable_cache=False)
    
    # Test basic text translation
    test_texts = [
        "Hello world",
        "The night is dark and full of terrors.",
        "Winter is coming.",
        "This is a very long sentence that should be more than five hundred characters to test the sentence splitting functionality of our improved translator. It contains multiple ideas and concepts that need to be properly translated while maintaining the original meaning and context. The sentence splitting should help improve translation quality by breaking down complex thoughts into manageable chunks that translation services can handle more effectively."
    ]
    
    print("Testing text translations:")
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Original: {text[:60]}{'...' if len(text) > 60 else ''}")
        try:
            translated = translator.translate_text(text)
            print(f"   Translated: {translated}")
            print("   ✅ Success")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Show statistics
    stats = translator.get_stats()
    print(f"\n📊 Translation Statistics:")
    print(f"   Total translations: {stats['total_translations']}")
    print(f"   Failed translations: {stats['failed_translations']}")
    print(f"   Success rate: {stats.get('success_rate', 0):.1%}")
    print(f"   Service usage: {stats['service_usage']}")

def test_subtitle_creation():
    """Test subtitle file creation and processing."""
    print("\n🎬 Testing subtitle file processing...")
    
    # Create a test SRT content
    test_srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello, this is a test subtitle.

2
00:00:05,000 --> 00:00:08,000
Winter is coming to Westeros.

3
00:00:09,000 --> 00:00:12,000
The night is dark and full of terrors.
"""
    
    # Write test file
    test_file = Path("test_sample.srt")
    test_file.write_text(test_srt_content)
    
    try:
        # Test processing
        translator = SubtitleTranslator(enable_cache=False)
        processor = SubtitleProcessor(translator)
        
        print(f"Processing test file: {test_file}")
        
        # Get file info
        info = processor.get_subtitle_info(test_file)
        print(f"File info: {info}")
        
        if info.get('total_entries', 0) > 0:
            print(f"✅ Successfully loaded {info['total_entries']} subtitle entries")
        else:
            print("❌ Failed to load subtitle entries")
        
    except Exception as e:
        print(f"❌ Error processing subtitle: {e}")
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            print("🧹 Cleaned up test file")

if __name__ == "__main__":
    print("🚀 Swahili Subtitle Translator - Basic Tests")
    print("=" * 50)
    
    try:
        test_basic_translation()
        test_subtitle_creation()
        print("\n🎉 All basic tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
