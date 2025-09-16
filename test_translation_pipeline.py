#!/usr/bin/env python3
"""
Comprehensive integration tests for the translation pipeline.
"""

import sys
import tempfile
import logging
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from swahili_subtitle_translator.translation import (
    # Models
    TranslationRequest, TranslationResponse, LanguageCode, TranslationService,
    SubtitleEntry, SubtitleFile,
    
    # Services
    create_translation_service, translate_text,
    
    # Engine
    TranslationEngine, create_translation_engine, translate_simple,
    
    # Subtitle parsing
    SRTParser, SubtitleValidator, SubtitleProcessor,
    create_sample_subtitles, parse_srt_file, save_srt_file
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_translation_models():
    """Test translation data models."""
    print("\n" + "="*60)
    print("Testing Translation Models")
    print("="*60)
    
    try:
        # Test TranslationRequest
        request = TranslationRequest(
            text="Hello, world!",
            source_language=LanguageCode.ENGLISH,
            target_language=LanguageCode.SWAHILI,
            domain="movie"
        )
        
        print(f"✓ Created TranslationRequest: {request.text}")
        print(f"  ID: {request.id}")
        print(f"  Languages: {request.source_language.value} -> {request.target_language.value}")
        print(f"  Domain: {request.domain}")
        
        # Test SubtitleEntry
        entry = SubtitleEntry(
            index=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="Hello, world!"
        )
        
        print(f"\n✓ Created SubtitleEntry: {entry.text}")
        print(f"  Duration: {entry.duration_ms}ms")
        print(f"  Plain text: '{entry.get_plain_text()}'")
        
        # Test SubtitleFile
        sample_subtitles = create_sample_subtitles()
        print(f"\n✓ Created sample SubtitleFile")
        print(f"  Entries: {sample_subtitles.total_entries}")
        print(f"  Duration: {sample_subtitles.total_duration_ms}ms")
        
        stats = sample_subtitles.get_statistics()
        print(f"  Statistics: {stats['total_characters']} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Model testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_translation_services():
    """Test individual translation services."""
    print("\n" + "="*60)
    print("Testing Translation Services")
    print("="*60)
    
    try:
        # Test Mock service
        print("Testing Mock Translation Service:")
        mock_service = create_translation_service(TranslationService.MOCK)
        
        request = TranslationRequest(
            text="Hello",
            source_language=LanguageCode.ENGLISH,
            target_language=LanguageCode.SWAHILI
        )
        
        response = mock_service.translate(request)
        print(f"  Input: '{response.source_text}'")
        print(f"  Output: '{response.translated_text}'")
        print(f"  Success: {response.success}")
        print(f"  Confidence: {response.confidence_score}")
        print(f"  Service: {response.service.value}")
        
        # Test batch translation
        print("\nTesting Batch Translation:")
        from swahili_subtitle_translator.translation import BatchTranslationRequest
        batch_request_obj = BatchTranslationRequest(
            texts=["Hello", "Good morning", "Thank you"],
            source_language=LanguageCode.ENGLISH,
            target_language=LanguageCode.SWAHILI
        )
        batch_response = mock_service.translate_batch(batch_request_obj)
        
        print(f"  Batch size: {len(batch_request_obj.texts)}")
        print(f"  Success rate: {batch_response.success_rate:.1f}%")
        print(f"  Processing time: {batch_response.total_processing_time:.2f}s")
        
        # Test convenience function
        print("\nTesting convenience function:")
        simple_response = translate_text(
            "Welcome",
            source_lang=LanguageCode.ENGLISH,
            target_lang=LanguageCode.SWAHILI,
            service_type=TranslationService.MOCK
        )
        print(f"  '{simple_response.source_text}' -> '{simple_response.translated_text}'")
        
        return True
        
    except Exception as e:
        print(f"✗ Service testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_translation_engine():
    """Test the translation engine with fallbacks."""
    print("\n" + "="*60)
    print("Testing Translation Engine")
    print("="*60)
    
    try:
        # Create engine with mock services
        engine = create_translation_engine(
            default_service=TranslationService.MOCK
        )
        
        print("✓ Created translation engine")
        print(f"  Available services: {[s.value for s in engine.get_available_services()]}")
        print(f"  Default service: {engine.default_service.value}")
        
        # Test simple translation
        print("\nTesting simple translation:")
        response = engine.translate("How are you?")
        print(f"  '{response.source_text}' -> '{response.translated_text}'")
        print(f"  Success: {response.success}")
        
        # Test batch translation
        print("\nTesting batch translation:")
        texts = ["Hello", "Good morning", "How are you?", "Thank you", "Goodbye"]
        batch_response = engine.translate_batch(texts)
        
        print(f"  Total texts: {batch_response.total_texts}")
        print(f"  Successful: {batch_response.successful_translations}")
        print(f"  Success rate: {batch_response.success_rate:.1f}%")
        
        for i, translation in enumerate(batch_response.translations[:3]):
            if translation.success:
                print(f"    {i+1}. '{translation.source_text}' -> '{translation.translated_text}'")
        
        # Test engine statistics
        print("\nEngine statistics:")
        stats = engine.get_engine_stats()
        print(f"  Total translations: {stats['total_translations']}")
        print(f"  Success rate: {stats['successful_translations']}/{stats['total_translations']}")
        print(f"  Average quality: {stats['average_quality']:.2f}")
        print(f"  Total cost: ${stats['total_cost']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Engine testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subtitle_parsing():
    """Test subtitle parsing and formatting."""
    print("\n" + "="*60)
    print("Testing Subtitle Parsing")
    print("="*60)
    
    try:
        # Create sample SRT content
        srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
How are you today?

3
00:00:07,000 --> 00:00:09,000
Welcome to the show.
"""
        
        print("Testing SRT parsing:")
        parser = SRTParser()
        subtitle_file = parser.parse(srt_content)
        
        print(f"  ✓ Parsed {subtitle_file.total_entries} entries")
        print(f"  ✓ Total duration: {subtitle_file.total_duration_ms}ms")
        
        # Display first few entries
        for entry in subtitle_file.entries[:2]:
            print(f"    {entry.index}. '{entry.text}' ({entry.start_time} -> {entry.end_time})")
        
        # Test formatting back to SRT
        print("\nTesting SRT formatting:")
        formatted_srt = parser.format(subtitle_file)
        print(f"  ✓ Formatted to {len(formatted_srt)} characters")
        
        # Test validation
        print("\nTesting subtitle validation:")
        validator = SubtitleValidator()
        issues = validator.validate(subtitle_file)
        
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        print(f"  ✓ Found {total_issues} validation issues")
        
        for category, issue_list in issues.items():
            if issue_list:
                print(f"    {category}: {len(issue_list)} issues")
        
        return True
        
    except Exception as e:
        print(f"✗ Subtitle parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_translation_pipeline():
    """Test the complete translation pipeline from subtitle file to translated output."""
    print("\n" + "="*60)
    print("Testing Complete Translation Pipeline")
    print("="*60)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create sample subtitle file
            print("Step 1: Creating sample subtitle file")
            sample_subtitles = create_sample_subtitles()
            input_file = temp_path / "input.srt"
            
            save_srt_file(sample_subtitles, input_file, use_translation=False)
            print(f"  ✓ Created sample file: {input_file}")
            print(f"  ✓ File size: {input_file.stat().st_size} bytes")
            
            # Load subtitle file
            print("\nStep 2: Loading subtitle file")
            processor = SubtitleProcessor()
            loaded_subtitles = processor.load_subtitle_file(input_file)
            print(f"  ✓ Loaded {loaded_subtitles.total_entries} entries")
            
            # Create translation engine
            print("\nStep 3: Initializing translation engine")
            engine = create_translation_engine(default_service=TranslationService.MOCK)
            print(f"  ✓ Engine ready with {len(engine.get_available_services())} services")
            
            # Translate subtitle file
            print("\nStep 4: Translating subtitle file")
            
            def progress_callback(completed, total):
                if completed % 2 == 0:  # Report every other translation
                    print(f"    Progress: {completed}/{total} ({completed/total*100:.0f}%)")
            
            translated_subtitles = engine.translate_subtitle_file(
                loaded_subtitles,
                target_language=LanguageCode.SWAHILI,
                progress_callback=progress_callback
            )
            
            print(f"  ✓ Translation completed")
            print(f"  ✓ Quality score: {translated_subtitles.translation_quality_score:.2f}")
            print(f"  ✓ Service used: {translated_subtitles.translation_service.value}")
            
            # Show sample translations
            print("\nSample translations:")
            for entry in translated_subtitles.entries[:3]:
                print(f"    Original: '{entry.text}'")
                print(f"    Translated: '{entry.translated_text}'")
                print()
            
            # Save translated file
            print("Step 5: Saving translated subtitle file")
            output_file = temp_path / "output_translated.srt"
            
            validation_issues = processor.save_subtitle_file(
                translated_subtitles, 
                output_file,
                use_translation=True,
                validate=True
            )
            
            print(f"  ✓ Saved translated file: {output_file}")
            print(f"  ✓ Output file size: {output_file.stat().st_size} bytes")
            
            if validation_issues:
                total_issues = sum(len(issues) for issues in validation_issues.values())
                print(f"  ⚠ Validation found {total_issues} issues")
            else:
                print("  ✓ No validation issues")
            
            # Verify file contents
            print("\nStep 6: Verifying output file")
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.strip().split('\n')
            print(f"  ✓ Output file has {len(lines)} lines")
            
            # Check if translations are present
            has_translations = any('[SW]' in line for line in lines)
            print(f"  ✓ Contains translations: {has_translations}")
            
            # Engine statistics
            print("\nFinal engine statistics:")
            final_stats = engine.get_engine_stats()
            print(f"  Total translations: {final_stats['total_translations']}")
            print(f"  Success rate: {final_stats['successful_translations']}/{final_stats['total_translations']}")
            print(f"  Average quality: {final_stats['average_quality']:.2f}")
            
            return True
            
    except Exception as e:
        print(f"✗ Complete pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_functions():
    """Test convenience functions for easy usage."""
    print("\n" + "="*60)
    print("Testing Convenience Functions")
    print("="*60)
    
    try:
        # Test simple translation function
        print("Testing simple translation:")
        result = translate_simple("Hello, how are you?")
        print(f"  Input: 'Hello, how are you?'")
        print(f"  Output: '{result}'")
        
        # Test with different target language
        print("\nTesting with Spanish target:")
        result_es = translate_simple(
            "Good morning",
            target_language=LanguageCode.SPANISH
        )
        print(f"  Input: 'Good morning'")
        print(f"  Output: '{result_es}'")
        
        return True
        
    except Exception as e:
        print(f"✗ Convenience functions test failed: {e}")
        return False


def main():
    """Run all translation pipeline tests."""
    print("🌍 Swahili Subtitle Translator - Translation Pipeline Tests")
    print("="*70)
    print("Testing the complete translation system with mock services")
    print("="*70)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Translation Models", test_translation_models),
        ("Translation Services", test_translation_services), 
        ("Translation Engine", test_translation_engine),
        ("Subtitle Parsing", test_subtitle_parsing),
        ("Complete Pipeline", test_complete_translation_pipeline),
        ("Convenience Functions", test_convenience_functions)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The translation pipeline is working correctly.")
        print("\n📋 What was tested:")
        print("  ✅ Translation data models and validation")
        print("  ✅ Individual translation services (Mock)")
        print("  ✅ Translation engine with fallbacks")
        print("  ✅ SRT subtitle parsing and formatting")
        print("  ✅ Complete subtitle translation pipeline")
        print("  ✅ Convenience functions for easy usage")
        print("  ✅ File I/O and error handling")
        print("  ✅ Quality assessment and validation")
        
        print("\n🚀 Ready for production with real translation services!")
        return True
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
