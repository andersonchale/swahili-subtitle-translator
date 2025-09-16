"""
Command-line interface for Swahili Subtitle Translator.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List

from .config import get_config_manager, get_config, create_sample_config, ConfigManager
from .search import (
    SubtitleSearchEngine, search_subtitles, SourceType, SearchQuery
)
from .translation import (
    TranslationEngine, create_translation_engine, 
    TranslationService, LanguageCode, 
    SubtitleProcessor, parse_srt_file, save_srt_file
)
from .utils.exceptions import SubtitleTranslatorError

logger = logging.getLogger(__name__)


class CLIError(SubtitleTranslatorError):
    """CLI-specific errors."""
    pass


def print_colored(text: str, color: str = "white", config=None):
    """Print colored text if colors are enabled."""
    if config is None:
        config = get_config()
    if not config.colored_output:
        print(text)
        return
    
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    
    color_code = colors.get(color, colors["white"])
    print(f"{color_code}{text}{colors['reset']}")


def progress_callback(completed: int, total: int, config=None):
    """Progress callback for long operations."""
    if config is None:
        config = get_config()
    if config.show_progress:
        percentage = (completed / total) * 100 if total > 0 else 0
        print(f"Progress: {completed}/{total} ({percentage:.1f}%)")


def search_command(args, config_manager=None):
    """Handle subtitle search command."""
    print_colored("\n🔍 Searching for subtitles...", "blue")
    
    try:
        # Get configuration
        if config_manager is None:
            config_manager = get_config_manager()
        config = config_manager.get_config()
        
        # Create search engine
        search_engine = SubtitleSearchEngine(
            opensubtitles_api_key=config.search.opensubtitles_api_key
        )
        
        # Create search query
        query = SearchQuery(
            title=args.title,
            language=args.language or config.default_source_language,
            year=args.year,
            season=args.season,
            episode=args.episode,
            limit=args.limit or config.search.max_results
        )
        
        # Determine sources to search
        sources = None
        if args.sources:
            try:
                sources = [SourceType(source) for source in args.sources]
            except ValueError as e:
                print_colored(f"Invalid source: {e}", "red")
                return 1
        
        # Perform search
        results = search_engine.search(query, sources=sources)
        
        if not results:
            print_colored("No subtitles found.", "yellow")
            return 0
        
        # Display results
        print_colored(f"\nFound {len(results)} subtitle(s):", "green")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.display_name}")
            print(f"   Source: {result.source.value}")
            print(f"   Language: {result.language}")
            print(f"   Format: {result.format.value}")
            if result.release_info:
                print(f"   Release: {result.release_info}")
            if result.download_count:
                print(f"   Downloads: {result.download_count:,}")
            print(f"   URL: {result.download_url}")
        
        # Download if requested
        if args.download:
            download_dir = Path(args.output or config.search.download_directory)
            
            for i, result in enumerate(results):
                try:
                    output_file = download_dir / f"{result.title}_{result.source.value}.srt"
                    downloaded_path = search_engine.download_subtitle(result, output_file)
                    print_colored(f"✓ Downloaded: {downloaded_path}", "green")
                except Exception as e:
                    print_colored(f"✗ Download failed for {result.title}: {e}", "red")
        
        return 0
        
    except Exception as e:
        print_colored(f"Search failed: {e}", "red")
        logger.error(f"Search command failed: {e}")
        return 1


def translate_command(args, config_manager=None):
    """Handle subtitle translation command."""
    print_colored("\n🌍 Translating subtitles...", "blue")
    
    try:
        # Get configuration
        if config_manager is None:
            config_manager = get_config_manager()
        config = config_manager.get_config()
        
        # Validate input file
        input_file = Path(args.input)
        if not input_file.exists():
            print_colored(f"Input file not found: {input_file}", "red")
            return 1
        
        # Create translation engine
        engine_config = {}
        if config.translation.google_api_key:
            engine_config['google_api_key'] = config.translation.google_api_key
        if config.translation.openai_api_key:
            engine_config['openai_api_key'] = config.translation.openai_api_key
        
        # Determine service
        service_name = args.service or config.translation.default_service
        try:
            service = TranslationService(service_name)
        except ValueError:
            print_colored(f"Invalid translation service: {service_name}", "red")
            return 1
        
        engine = create_translation_engine(
            default_service=service,
            **engine_config
        )
        
        # Load subtitle file
        print_colored(f"Loading subtitle file: {input_file}", "cyan")
        processor = SubtitleProcessor()
        subtitle_file = processor.load_subtitle_file(input_file)
        
        print_colored(f"Loaded {subtitle_file.total_entries} subtitle entries", "cyan")
        
        # Determine target language
        target_lang = args.target_language or config.default_target_language
        try:
            target_language = LanguageCode(target_lang)
        except ValueError:
            print_colored(f"Invalid target language: {target_lang}", "red")
            return 1
        
        # Translate subtitle file
        print_colored(f"Translating to {target_language.value}...", "cyan")
        
        translated_file = engine.translate_subtitle_file(
            subtitle_file,
            target_language=target_language,
            preferred_service=service,
            progress_callback=progress_callback if config.show_progress else None
        )
        
        # Save translated file
        output_file = Path(args.output) if args.output else input_file.with_suffix(f'.{target_lang}.srt')
        
        validation_issues = processor.save_subtitle_file(
            translated_file,
            output_file,
            use_translation=True,
            validate=not args.no_validate
        )
        
        print_colored(f"✓ Translation completed: {output_file}", "green")
        
        # Display statistics
        stats = engine.get_engine_stats()
        quality_score = translated_file.translation_quality_score
        
        print_colored("\nTranslation Statistics:", "cyan")
        print(f"  Service used: {translated_file.translation_service.value}")
        print(f"  Quality score: {quality_score:.2f}" if quality_score else "  Quality score: N/A")
        print(f"  Total translations: {stats['total_translations']}")
        print(f"  Success rate: {stats['successful_translations']}/{stats['total_translations']}")
        if stats['total_cost'] > 0:
            print(f"  Estimated cost: ${stats['total_cost']:.4f}")
        
        # Display validation issues
        if validation_issues and not args.no_validate:
            total_issues = sum(len(issues) for issues in validation_issues.values())
            if total_issues > 0:
                print_colored(f"\n⚠ Found {total_issues} validation issues:", "yellow")
                for category, issues in validation_issues.items():
                    if issues:
                        print(f"  {category.title()}: {len(issues)}")
                        if args.verbose:
                            for issue in issues[:3]:  # Show first 3 issues
                                print(f"    - {issue}")
        
        return 0
        
    except Exception as e:
        print_colored(f"Translation failed: {e}", "red")
        logger.error(f"Translation command failed: {e}")
        return 1


def pipeline_command(args, config_manager=None):
    """Handle complete pipeline: search + download + translate."""
    print_colored("\n🚀 Running complete subtitle pipeline...", "blue")
    
    # Step 1: Search
    print_colored("Step 1: Searching for subtitles", "cyan")
    search_args = argparse.Namespace(
        title=args.title,
        language=args.source_language,
        year=args.year,
        season=args.season,
        episode=args.episode,
        limit=args.limit,
        sources=args.sources,
        download=True,
        output=args.temp_dir or "./temp"
    )
    
    result = search_command(search_args)
    if result != 0:
        return result
    
    # Find downloaded files
    temp_dir = Path(args.temp_dir or "./temp")
    srt_files = list(temp_dir.glob("*.srt"))
    
    if not srt_files:
        print_colored("No subtitle files were downloaded", "red")
        return 1
    
    # Step 2: Translate first file
    print_colored(f"\nStep 2: Translating {srt_files[0]}", "cyan")
    translate_args = argparse.Namespace(
        input=str(srt_files[0]),
        output=args.output,
        service=args.service,
        target_language=args.target_language,
        no_validate=args.no_validate,
        verbose=args.verbose
    )
    
    result = translate_command(translate_args)
    
    # Cleanup temp files if requested
    if args.cleanup and not args.temp_dir:
        for file in srt_files:
            file.unlink()
        temp_dir.rmdir()
        print_colored("✓ Cleaned up temporary files", "cyan")
    
    return result


def config_command(args, config_manager=None):
    """Handle configuration management."""
    if config_manager is None:
        config_manager = get_config_manager()
    
    if args.action == "show":
        config_manager.print_config_summary()
        
        # Show validation issues
        issues = config_manager.validate_config()
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        
        if total_issues > 0:
            print_colored(f"\nConfiguration Issues:", "yellow")
            for category, issue_list in issues.items():
                if issue_list:
                    print_colored(f"{category.title()}:", "cyan")
                    for issue in issue_list:
                        print(f"  - {issue}")
    
    elif args.action == "create":
        config_path = Path(args.file) if args.file else config_manager.config_file
        create_sample_config(config_path)
    
    elif args.action == "validate":
        issues = config_manager.validate_config()
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        
        if total_issues == 0:
            print_colored("✓ Configuration is valid", "green")
        else:
            print_colored(f"Found {total_issues} configuration issues:", "yellow")
            for category, issue_list in issues.items():
                if issue_list:
                    print_colored(f"{category.title()}:", "cyan")
                    for issue in issue_list:
                        print(f"  - {issue}")
        
        return 1 if any(issues['errors']) else 0
    
    return 0


def test_command(args, config_manager=None):
    """Handle service testing."""
    print_colored("\n🧪 Testing services...", "blue")
    
    try:
        if config_manager is None:
            config_manager = get_config_manager()
        config = config_manager.get_config()
        
        # Test search services
        print_colored("Testing search services:", "cyan")
        search_engine = SubtitleSearchEngine(
            opensubtitles_api_key=config.search.opensubtitles_api_key
        )
        search_results = search_engine.test_sources("The Matrix")
        
        for source, success in search_results.items():
            status = "✓" if success else "✗"
            color = "green" if success else "red"
            print_colored(f"  {status} {source.value}", color)
        
        # Test translation services
        print_colored("\nTesting translation services:", "cyan")
        engine_config = {}
        if config.translation.google_api_key:
            engine_config['google_api_key'] = config.translation.google_api_key
        if config.translation.openai_api_key:
            engine_config['openai_api_key'] = config.translation.openai_api_key
        
        translation_engine = create_translation_engine(**engine_config)
        translation_results = translation_engine.test_services("Hello world")
        
        for service, success in translation_results.items():
            status = "✓" if success else "✗"
            color = "green" if success else "red"
            print_colored(f"  {status} {service.value}", color)
        
        # Summary
        total_search = len(search_results)
        working_search = sum(search_results.values())
        total_translation = len(translation_results)
        working_translation = sum(translation_results.values())
        
        print_colored(f"\nSummary:", "cyan")
        print(f"  Search: {working_search}/{total_search} services working")
        print(f"  Translation: {working_translation}/{total_translation} services working")
        
        return 0
        
    except Exception as e:
        print_colored(f"Testing failed: {e}", "red")
        return 1


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="swahili-translator",
        description="Search, download, and translate subtitles to Swahili",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for subtitles
  swahili-translator search "The Matrix" --limit 5
  
  # Search and download
  swahili-translator search "Avatar" --download --output ./downloads
  
  # Translate a subtitle file
  swahili-translator translate movie.srt --service google_translate
  
  # Complete pipeline: search, download, and translate
  swahili-translator pipeline "Inception" --target-language sw
  
  # Test all services
  swahili-translator test
  
  # Show configuration
  swahili-translator config show
        """
    )
    
    # Global options
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for subtitles")
    search_parser.add_argument("title", help="Movie or TV show title")
    search_parser.add_argument("--language", "-l", help="Source language (default: en)")
    search_parser.add_argument("--year", "-y", type=int, help="Release year")
    search_parser.add_argument("--season", "-s", type=int, help="TV show season")
    search_parser.add_argument("--episode", "-e", type=int, help="TV show episode")
    search_parser.add_argument("--limit", type=int, help="Maximum results")
    search_parser.add_argument("--sources", nargs="+", 
                             choices=["opensubtitles", "subscene", "yify"],
                             help="Sources to search")
    search_parser.add_argument("--download", "-d", action="store_true", help="Download subtitles")
    search_parser.add_argument("--output", "-o", help="Output directory")
    search_parser.set_defaults(func=search_command)
    
    # Translate command
    translate_parser = subparsers.add_parser("translate", help="Translate subtitle file")
    translate_parser.add_argument("input", help="Input subtitle file")
    translate_parser.add_argument("--output", "-o", help="Output file path")
    translate_parser.add_argument("--service", choices=["google_translate", "openai_gpt", "offline_model", "mock"],
                                help="Translation service")
    translate_parser.add_argument("--target-language", "-t", default="sw",
                                help="Target language (default: sw)")
    translate_parser.add_argument("--no-validate", action="store_true", help="Skip validation")
    translate_parser.set_defaults(func=translate_command)
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Complete search and translate pipeline")
    pipeline_parser.add_argument("title", help="Movie or TV show title")
    pipeline_parser.add_argument("--output", "-o", help="Output file path")
    pipeline_parser.add_argument("--source-language", default="en", help="Source language")
    pipeline_parser.add_argument("--target-language", "-t", default="sw", help="Target language")
    pipeline_parser.add_argument("--service", choices=["google_translate", "openai_gpt", "offline_model", "mock"],
                                help="Translation service")
    pipeline_parser.add_argument("--year", "-y", type=int, help="Release year")
    pipeline_parser.add_argument("--season", "-s", type=int, help="TV show season")
    pipeline_parser.add_argument("--episode", "-e", type=int, help="TV show episode")
    pipeline_parser.add_argument("--limit", type=int, default=1, help="Maximum search results")
    pipeline_parser.add_argument("--sources", nargs="+",
                               choices=["opensubtitles", "subscene", "yify"],
                               help="Sources to search")
    pipeline_parser.add_argument("--temp-dir", help="Temporary directory for downloads")
    pipeline_parser.add_argument("--cleanup", action="store_true", help="Clean up temporary files")
    pipeline_parser.add_argument("--no-validate", action="store_true", help="Skip validation")
    pipeline_parser.set_defaults(func=pipeline_command)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("action", choices=["show", "create", "validate"],
                             help="Configuration action")
    config_parser.add_argument("--file", help="Configuration file path")
    config_parser.set_defaults(func=config_command)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test all services")
    test_parser.set_defaults(func=test_command)
    
    return parser


def _handle_backward_compatibility():
    """Handle backward compatibility by detecting subtitle files and inserting translate command."""
    if len(sys.argv) < 2:
        return
    
    # Check if we already have a subcommand
    valid_commands = {'search', 'translate', 'pipeline', 'config', 'test'}
    
    # Find first non-option argument
    skip_next = False
    for i, arg in enumerate(sys.argv[1:], 1):
        if skip_next:
            skip_next = False
            continue
            
        if arg.startswith('-'):
            # Check if this option takes a value
            if arg in ('--config', '--verbose', '--debug', '--no-color'):
                if arg in ('--config',):  # Options that require values
                    skip_next = True
            continue
        elif arg in valid_commands:
            # Already has a subcommand
            return
        elif arg.endswith(('.srt', '.ass', '.vtt')):
            # Found subtitle file, insert 'translate' before it
            sys.argv.insert(i, 'translate')
            return
        else:
            # Found non-option, non-subtitle arg - let normal parsing handle it
            return


def main():
    """Main CLI entry point."""
    # Handle backward compatibility BEFORE parsing: if first non-option arg is a subtitle file, assume translate
    _handle_backward_compatibility()
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize configuration with specific config file if provided
        if args.config:
            from pathlib import Path
            config_manager = ConfigManager(config_file=Path(args.config))
        else:
            config_manager = get_config_manager()
        config = config_manager.get_config()
        
        # Override config with command line args
        if args.debug:
            config.debug = True
            config.log_level = "DEBUG"
        if args.verbose:
            config.verbose = True
        if args.no_color:
            config.colored_output = False
        
        # Setup logging
        config_manager.setup_logging()
        
        # Run the command with config manager
        return args.func(args, config_manager)
        
    except KeyboardInterrupt:
        print_colored("\n\nOperation cancelled by user", "yellow")
        return 130
    except Exception as e:
        print_colored(f"Unexpected error: {e}", "red")
        logger.exception("Unexpected error in main")
        return 1


if __name__ == "__main__":
    sys.exit(main())
