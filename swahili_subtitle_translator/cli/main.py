#!/usr/bin/env python3
"""
Swahili Subtitle Translator CLI

Professional command-line interface for translating subtitle files.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional
import colorama
from colorama import Fore, Style

from ..core.translator import SubtitleTranslator
from ..core.processor import SubtitleProcessor
from ..utils.formats import SupportedFormats, validate_subtitle_file
from ..utils.exceptions import SubtitleTranslatorError
from .. import __version__, __author__

# Initialize colorama for cross-platform colored output
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProgressBar:
    """Simple progress bar for CLI operations."""
    
    def __init__(self, total: int, width: int = 50):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, current: int, message: str = ""):
        """Update progress bar."""
        self.current = current
        progress = current / self.total if self.total > 0 else 0
        filled = int(progress * self.width)
        bar = '█' * filled + '░' * (self.width - filled)
        
        percent = int(progress * 100)
        
        # Clear line and print progress
        print(f'\r{Fore.CYAN}Progress: {bar} {percent}% {message}{Style.RESET_ALL}', 
              end='', flush=True)
        
        if current >= self.total:
            print()  # New line when complete


def print_banner():
    """Print application banner."""
    banner = f"""
{Fore.CYAN}╭───────────────────────────────────────────────────────────╮
│           Swahili Subtitle Translator v{__version__}               │
│              Professional Translation Tool                │
│                   Author: {__author__}                       │
╰───────────────────────────────────────────────────────────╯{Style.RESET_ALL}
"""
    print(banner)


def print_error(message: str):
    """Print error message."""
    print(f"{Fore.RED}✗ Error: {message}{Style.RESET_ALL}")


def print_success(message: str):
    """Print success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Fore.YELLOW}⚠ Warning: {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def validate_input_files(files: List[Path]) -> List[Path]:
    """Validate input subtitle files."""
    valid_files = []
    
    for file_path in files:
        if not file_path.exists():
            print_error(f"File not found: {file_path}")
            continue
        
        validation_result = validate_subtitle_file(file_path)
        
        if validation_result['valid']:
            valid_files.append(file_path)
            print_info(f"Valid {validation_result['format'].upper()} file: {file_path.name}")
            
            for warning in validation_result.get('warnings', []):
                print_warning(warning)
        else:
            print_error(f"Invalid subtitle file: {file_path}")
            for error in validation_result.get('errors', []):
                print_error(f"  - {error}")
    
    return valid_files


def translate_single_file(args) -> int:
    """Translate a single subtitle file."""
    input_path = Path(args.input)
    
    # Validate input file
    valid_files = validate_input_files([input_path])
    if not valid_files:
        return 1
    
    # Set output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_swahili{input_path.suffix}"
    
    try:
        # Initialize translator and processor
        translator = SubtitleTranslator(
            primary_service=args.service,
            enable_cache=not args.no_cache,
            max_retries=args.max_retries
        )
        
        processor = SubtitleProcessor(translator)
        
        print_info(f"Translating: {input_path}")
        print_info(f"Output: {output_path}")
        print_info(f"Service: {args.service}")
        
        # Progress tracking
        progress_bar = None
        
        def progress_callback(message):
            if "Translating:" in message:
                parts = message.split()
                if len(parts) >= 2:
                    current_total = parts[1].split('/')
                    if len(current_total) == 2:
                        current, total = map(int, current_total)
                        if progress_bar is None:
                            nonlocal progress_bar
                            progress_bar = ProgressBar(total)
                        progress_bar.update(current, f"Translating subtitles...")
        
        # Translate
        result_path = processor.translate_subtitles(
            input_path, 
            output_path,
            progress_callback=progress_callback
        )
        
        print_success(f"Translation completed: {result_path}")
        
        # Show translation statistics
        if args.stats:
            stats = translator.get_stats()
            print(f"\n{Fore.CYAN}Translation Statistics:{Style.RESET_ALL}")
            print(f"  Total translations: {stats['total_translations']}")
            print(f"  Cache hits: {stats['cache_hits']}")
            print(f"  Success rate: {stats.get('success_rate', 0):.1%}")
            print(f"  Service usage: {stats['service_usage']}")
        
        return 0
        
    except SubtitleTranslatorError as e:
        print_error(f"Translation failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def translate_batch(args) -> int:
    """Translate multiple subtitle files in a directory."""
    input_dir = Path(args.input)
    
    if not input_dir.exists():
        print_error(f"Directory not found: {input_dir}")
        return 1
    
    if not input_dir.is_dir():
        print_error(f"Path is not a directory: {input_dir}")
        return 1
    
    # Find subtitle files
    patterns = args.pattern if args.pattern else ["*.srt", "*.ass", "*.vtt", "*.sub"]
    subtitle_files = []
    
    for pattern in patterns:
        subtitle_files.extend(input_dir.glob(pattern))
    
    if not subtitle_files:
        print_error(f"No subtitle files found matching patterns: {patterns}")
        return 1
    
    # Validate files
    valid_files = validate_input_files(subtitle_files)
    if not valid_files:
        return 1
    
    print_info(f"Found {len(valid_files)} valid subtitle files")
    
    # Set output directory
    output_dir = Path(args.output) if args.output else input_dir / "translated_swahili"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize translator and processor
        translator = SubtitleTranslator(
            primary_service=args.service,
            enable_cache=not args.no_cache,
            max_retries=args.max_retries
        )
        
        processor = SubtitleProcessor(translator)
        
        print_info(f"Output directory: {output_dir}")
        print_info(f"Translation service: {args.service}")
        
        # Batch progress tracking
        overall_progress = ProgressBar(len(valid_files))
        
        def batch_progress_callback(message):
            if message.startswith("File"):
                # Extract file number from message like "File 1/5: ..."
                try:
                    parts = message.split(":")
                    file_part = parts[0].strip()  # "File 1/5"
                    file_info = file_part.split()[1]  # "1/5"
                    current_file = int(file_info.split('/')[0])
                    overall_progress.update(current_file, f"Processing files...")
                except:
                    pass
        
        # Translate batch
        translated_files = processor.batch_translate(
            input_dir,
            output_dir,
            file_pattern=args.pattern[0] if args.pattern else "*.srt",
            progress_callback=batch_progress_callback
        )
        
        print_success(f"Batch translation completed!")
        print_info(f"Translated {len(translated_files)} files:")
        
        for file_path in translated_files:
            print(f"  - {file_path.name}")
        
        # Show statistics
        if args.stats:
            stats = translator.get_stats()
            print(f"\n{Fore.CYAN}Batch Translation Statistics:{Style.RESET_ALL}")
            print(f"  Files processed: {len(translated_files)}")
            print(f"  Total translations: {stats['total_translations']}")
            print(f"  Cache hits: {stats['cache_hits']}")
            print(f"  Success rate: {stats.get('success_rate', 0):.1%}")
            print(f"  Service usage: {stats['service_usage']}")
        
        return 0
        
    except SubtitleTranslatorError as e:
        print_error(f"Batch translation failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def show_info(args) -> int:
    """Show information about subtitle files or formats."""
    if args.formats:
        # Show supported formats
        print(f"{Fore.CYAN}Supported Subtitle Formats:{Style.RESET_ALL}")
        
        formats = SupportedFormats.FORMATS
        for format_name, info in formats.items():
            status = "✓" if info['read'] else "✗"
            write_status = "✓" if info['write'] else "✗"
            
            print(f"  {Fore.GREEN}{format_name.upper()}{Style.RESET_ALL} - {info['name']}")
            print(f"    Extensions: {', '.join(info['extensions'])}")
            print(f"    Read: {status}  Write: {write_status}")
            print(f"    Description: {info['description']}")
            print()
        
        return 0
    
    if args.file:
        # Show file information
        file_path = Path(args.file)
        
        if not file_path.exists():
            print_error(f"File not found: {file_path}")
            return 1
        
        validation_result = validate_subtitle_file(file_path)
        
        print(f"{Fore.CYAN}Subtitle File Information:{Style.RESET_ALL}")
        print(f"  File: {file_path}")
        print(f"  Size: {validation_result.get('info', {}).get('file_size', 0)} bytes")
        print(f"  Format: {validation_result.get('format', 'Unknown')}")
        print(f"  Valid: {'✓' if validation_result['valid'] else '✗'}")
        
        if validation_result.get('errors'):
            print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
            for error in validation_result['errors']:
                print(f"  - {error}")
        
        if validation_result.get('warnings'):
            print(f"\n{Fore.YELLOW}Warnings:{Style.RESET_ALL}")
            for warning in validation_result['warnings']:
                print(f"  - {warning}")
        
        return 0
    
    print_error("No information requested. Use --formats or --file <path>")
    return 1


def manage_cache(args) -> int:
    """Manage translation cache."""
    try:
        from ..utils.cache import TranslationCache
        
        cache_dir = Path.home() / '.swahili_subtitle_translator' / 'cache'
        if args.cache_dir:
            cache_dir = Path(args.cache_dir)
        
        cache = TranslationCache(cache_dir)
        
        if args.clear_cache:
            cache.clear()
            print_success("Translation cache cleared")
        elif args.cache_stats:
            stats = cache.get_stats()
            print(f"{Fore.CYAN}Cache Statistics:{Style.RESET_ALL}")
            print(f"  Total entries: {stats.get('total_entries', 0)}")
            print(f"  Cache hits: {stats.get('hits', 0)}")
            print(f"  Cache misses: {stats.get('misses', 0)}")
            print(f"  Hit rate: {stats.get('hit_rate', 0):.1%}")
        else:
            print_error("No cache operation specified")
            return 1
        
        return 0
        
    except Exception as e:
        print_error(f"Cache operation failed: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Professional subtitle translation tool for English to Swahili",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Translate single file
  swahili-sub-translate movie.srt
  
  # Translate with custom output
  swahili-sub-translate movie.srt -o movie_swahili.srt
  
  # Batch translate directory
  swahili-sub-translate /path/to/subtitles --batch
  
  # Use MyMemory service instead of Google Translate
  swahili-sub-translate movie.srt --service mymemory
  
  # Show supported formats
  swahili-sub-translate --info --formats
  
  # Clear translation cache
  swahili-sub-translate --cache --clear

Version: {__version__}
Author: {__author__}
"""
    )
    
    # Main arguments
    parser.add_argument('input', nargs='?', 
                       help='Input subtitle file or directory')
    
    parser.add_argument('-o', '--output',
                       help='Output file or directory')
    
    parser.add_argument('--batch', action='store_true',
                       help='Batch mode: translate all files in directory')
    
    parser.add_argument('--service', choices=['google', 'mymemory'],
                       default='google',
                       help='Translation service to use (default: google)')
    
    parser.add_argument('--pattern', action='append',
                       help='File patterns for batch mode (e.g., *.srt)')
    
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable translation caching')
    
    parser.add_argument('--max-retries', type=int, default=3,
                       help='Maximum retry attempts for failed translations')
    
    parser.add_argument('--stats', action='store_true',
                       help='Show translation statistics')
    
    # Information commands
    info_group = parser.add_argument_group('Information')
    info_group.add_argument('--info', action='store_true',
                           help='Show information mode')
    info_group.add_argument('--formats', action='store_true',
                           help='Show supported subtitle formats')
    info_group.add_argument('--file',
                           help='Show information about specific file')
    
    # Cache management
    cache_group = parser.add_argument_group('Cache Management')
    cache_group.add_argument('--cache', action='store_true',
                            help='Cache management mode')
    cache_group.add_argument('--clear-cache', action='store_true',
                            help='Clear translation cache')
    cache_group.add_argument('--cache-stats', action='store_true',
                            help='Show cache statistics')
    cache_group.add_argument('--cache-dir',
                            help='Custom cache directory')
    
    # Debug options
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Quiet mode')
    
    parser.add_argument('--version', action='version', 
                       version=f'Swahili Subtitle Translator {__version__}')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging based on arguments
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Show banner unless in quiet mode
    if not args.quiet:
        print_banner()
    
    # Route to appropriate function
    try:
        if args.info:
            return show_info(args)
        elif args.cache:
            return manage_cache(args)
        elif not args.input:
            parser.print_help()
            return 1
        elif args.batch:
            return translate_batch(args)
        else:
            return translate_single_file(args)
            
    except KeyboardInterrupt:
        print_error("Operation cancelled by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
