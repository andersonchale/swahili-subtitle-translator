"""
Subtitle parser and formatter for various subtitle formats.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Union, TextIO, Dict, Tuple

from .models import SubtitleEntry, SubtitleFile, LanguageCode
from ..utils.exceptions import SubtitleTranslatorError

logger = logging.getLogger(__name__)


class SubtitleParserError(SubtitleTranslatorError):
    """Exception raised by subtitle parser."""
    pass


class SRTParser:
    """Parser for SRT (SubRip Text) subtitle format."""
    
    def __init__(self):
        self.encoding_priorities = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def parse(self, content: Union[str, bytes, Path, TextIO]) -> SubtitleFile:
        """
        Parse SRT content into SubtitleFile.
        
        Args:
            content: SRT content as string, bytes, file path, or file handle
            
        Returns:
            Parsed subtitle file
        """
        try:
            # Convert input to string
            if isinstance(content, Path):
                text_content = self._read_file(content)
                filename = content.name
            elif isinstance(content, (bytes, bytearray)):
                text_content = self._decode_bytes(content)
                filename = None
            elif hasattr(content, 'read'):  # File-like object
                text_content = content.read()
                filename = getattr(content, 'name', None)
            else:
                text_content = str(content)
                filename = None
            
            # Parse subtitle entries
            entries = self._parse_entries(text_content)
            
            # Create subtitle file
            subtitle_file = SubtitleFile(
                entries=entries,
                source_language=LanguageCode.ENGLISH,  # Default assumption
                filename=filename,
                format_type="srt",
                encoding="utf-8"
            )
            
            logger.info(f"Parsed SRT file with {len(entries)} entries")
            return subtitle_file
            
        except Exception as e:
            logger.error(f"SRT parsing failed: {e}")
            raise SubtitleParserError(f"Failed to parse SRT content: {e}")
    
    def _read_file(self, file_path: Path) -> str:
        """Read file with automatic encoding detection."""
        if not file_path.exists():
            raise SubtitleParserError(f"File does not exist: {file_path}")
        
        # Try different encodings
        for encoding in self.encoding_priorities:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.debug(f"Successfully read file with {encoding} encoding")
                return content
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # If all encodings fail, use utf-8 with error handling
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            logger.warning("Used UTF-8 with error replacement for file reading")
            return content
        except Exception as e:
            raise SubtitleParserError(f"Could not read file with any encoding: {e}")
    
    def _decode_bytes(self, content: bytes) -> str:
        """Decode bytes with automatic encoding detection."""
        for encoding in self.encoding_priorities:
            try:
                return content.decode(encoding)
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # Fallback with error replacement
        return content.decode('utf-8', errors='replace')
    
    def _parse_entries(self, content: str) -> List[SubtitleEntry]:
        """Parse subtitle entries from SRT content."""
        entries = []
        
        # Split content into blocks (separated by double newlines)
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
            
            entry = self._parse_single_entry(block)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _parse_single_entry(self, block: str) -> Optional[SubtitleEntry]:
        """Parse a single subtitle entry from a block of text."""
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        
        if len(lines) < 3:
            logger.debug(f"Skipping invalid block with {len(lines)} lines")
            return None
        
        try:
            # First line: sequence number
            index = int(lines[0])
            
            # Second line: timestamps
            timestamp_line = lines[1]
            start_time, end_time = self._parse_timestamps(timestamp_line)
            
            # Remaining lines: subtitle text
            text_lines = lines[2:]
            text = '\n'.join(text_lines)
            
            return SubtitleEntry(
                index=index,
                start_time=start_time,
                end_time=end_time,
                text=text
            )
            
        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse subtitle block: {e}")
            return None
    
    def _parse_timestamps(self, timestamp_line: str) -> Tuple[str, str]:
        """Parse timestamp line into start and end times."""
        # SRT format: "00:01:23,456 --> 00:01:25,789"
        timestamp_pattern = r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})'
        
        match = re.match(timestamp_pattern, timestamp_line)
        if not match:
            raise ValueError(f"Invalid timestamp format: {timestamp_line}")
        
        start_time, end_time = match.groups()
        return start_time, end_time
    
    def format(self, subtitle_file: SubtitleFile, use_translation: bool = True) -> str:
        """
        Format SubtitleFile back to SRT string.
        
        Args:
            subtitle_file: Subtitle file to format
            use_translation: Whether to use translated text
            
        Returns:
            SRT formatted string
        """
        if not subtitle_file.entries:
            return ""
        
        srt_blocks = []
        
        for entry in subtitle_file.entries:
            # Choose text to use
            if use_translation and entry.translated_text:
                text = entry.translated_text
            else:
                text = entry.text
            
            # Format entry
            srt_block = f"{entry.index}\n{entry.start_time} --> {entry.end_time}\n{text}\n"
            srt_blocks.append(srt_block)
        
        return '\n'.join(srt_blocks)
    
    def save(self, subtitle_file: SubtitleFile, output_path: Path, 
             use_translation: bool = True, encoding: str = 'utf-8'):
        """
        Save SubtitleFile as SRT file.
        
        Args:
            subtitle_file: Subtitle file to save
            output_path: Output file path
            use_translation: Whether to use translated text
            encoding: File encoding
        """
        try:
            content = self.format(subtitle_file, use_translation)
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(output_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"Saved SRT file: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save SRT file: {e}")
            raise SubtitleParserError(f"Failed to save SRT file: {e}")


class SubtitleValidator:
    """Validator for subtitle files."""
    
    def __init__(self):
        self.validation_rules = {
            'timing': True,
            'text_length': True,
            'overlap': True,
            'gaps': True
        }
    
    def validate(self, subtitle_file: SubtitleFile) -> Dict[str, List[str]]:
        """
        Validate subtitle file and return issues.
        
        Args:
            subtitle_file: Subtitle file to validate
            
        Returns:
            Dictionary with validation issues by category
        """
        issues = {
            'timing': [],
            'text_length': [],
            'overlap': [],
            'gaps': [],
            'general': []
        }
        
        if not subtitle_file.entries:
            issues['general'].append("No subtitle entries found")
            return issues
        
        # Check timing issues
        if self.validation_rules['timing']:
            self._check_timing_issues(subtitle_file, issues)
        
        # Check text length issues
        if self.validation_rules['text_length']:
            self._check_text_length_issues(subtitle_file, issues)
        
        # Check overlaps
        if self.validation_rules['overlap']:
            self._check_overlap_issues(subtitle_file, issues)
        
        # Check gaps
        if self.validation_rules['gaps']:
            self._check_gap_issues(subtitle_file, issues)
        
        return issues
    
    def _check_timing_issues(self, subtitle_file: SubtitleFile, issues: Dict):
        """Check for timing-related issues."""
        for entry in subtitle_file.entries:
            # Check if duration is reasonable
            duration_ms = entry.duration_ms
            
            if duration_ms <= 0:
                issues['timing'].append(f"Entry {entry.index}: Zero or negative duration")
            elif duration_ms < 200:  # Less than 200ms
                issues['timing'].append(f"Entry {entry.index}: Very short duration ({duration_ms}ms)")
            elif duration_ms > 10000:  # More than 10 seconds
                issues['timing'].append(f"Entry {entry.index}: Very long duration ({duration_ms}ms)")
    
    def _check_text_length_issues(self, subtitle_file: SubtitleFile, issues: Dict):
        """Check for text length issues."""
        for entry in subtitle_file.entries:
            text = entry.get_plain_text()
            
            if not text.strip():
                issues['text_length'].append(f"Entry {entry.index}: Empty text")
            elif len(text) > 200:  # Typical subtitle length limit
                issues['text_length'].append(f"Entry {entry.index}: Text too long ({len(text)} chars)")
    
    def _check_overlap_issues(self, subtitle_file: SubtitleFile, issues: Dict):
        """Check for overlapping subtitles."""
        entries = subtitle_file.entries
        
        for i in range(len(entries) - 1):
            current = entries[i]
            next_entry = entries[i + 1]
            
            current_end = current._time_to_ms(current.end_time)
            next_start = next_entry._time_to_ms(next_entry.start_time)
            
            if current_end > next_start:
                overlap_ms = current_end - next_start
                issues['overlap'].append(
                    f"Entries {current.index}-{next_entry.index}: Overlap of {overlap_ms}ms"
                )
    
    def _check_gap_issues(self, subtitle_file: SubtitleFile, issues: Dict):
        """Check for large gaps between subtitles."""
        entries = subtitle_file.entries
        
        for i in range(len(entries) - 1):
            current = entries[i]
            next_entry = entries[i + 1]
            
            current_end = current._time_to_ms(current.end_time)
            next_start = next_entry._time_to_ms(next_entry.start_time)
            
            gap_ms = next_start - current_end
            
            # Flag gaps longer than 5 seconds
            if gap_ms > 5000:
                gap_seconds = gap_ms / 1000
                issues['gaps'].append(
                    f"Entries {current.index}-{next_entry.index}: Large gap of {gap_seconds:.1f}s"
                )


class SubtitleProcessor:
    """High-level subtitle processing utilities."""
    
    def __init__(self):
        self.srt_parser = SRTParser()
        self.validator = SubtitleValidator()
    
    def load_subtitle_file(self, file_path: Union[str, Path]) -> SubtitleFile:
        """
        Load subtitle file with automatic format detection.
        
        Args:
            file_path: Path to subtitle file
            
        Returns:
            Loaded subtitle file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise SubtitleParserError(f"File does not exist: {file_path}")
        
        # Determine format by extension
        ext = file_path.suffix.lower()
        
        if ext == '.srt':
            return self.srt_parser.parse(file_path)
        else:
            raise SubtitleParserError(f"Unsupported subtitle format: {ext}")
    
    def save_subtitle_file(self, subtitle_file: SubtitleFile, output_path: Union[str, Path],
                          use_translation: bool = True, validate: bool = True) -> Optional[Dict]:
        """
        Save subtitle file with optional validation.
        
        Args:
            subtitle_file: Subtitle file to save
            output_path: Output file path
            use_translation: Whether to use translated text
            validate: Whether to validate before saving
            
        Returns:
            Validation issues if validation is enabled, None otherwise
        """
        output_path = Path(output_path)
        
        # Validate if requested
        validation_issues = None
        if validate:
            validation_issues = self.validator.validate(subtitle_file)
            
            # Log validation issues
            total_issues = sum(len(issues) for issues in validation_issues.values())
            if total_issues > 0:
                logger.warning(f"Found {total_issues} validation issues")
                for category, issues in validation_issues.items():
                    if issues:
                        logger.debug(f"{category.title()} issues: {len(issues)}")
        
        # Determine format and save
        ext = output_path.suffix.lower()
        
        if ext == '.srt':
            self.srt_parser.save(subtitle_file, output_path, use_translation)
        else:
            raise SubtitleParserError(f"Unsupported output format: {ext}")
        
        return validation_issues
    
    def create_sample_subtitle(self, text_pairs: List[Tuple[str, str]], 
                              base_time: str = "00:00:00,000") -> SubtitleFile:
        """
        Create a sample subtitle file from text pairs.
        
        Args:
            text_pairs: List of (start_time_offset, text) pairs
            base_time: Base start time
            
        Returns:
            Created subtitle file
        """
        entries = []
        
        for i, (duration_offset, text) in enumerate(text_pairs, 1):
            # Calculate start and end times
            start_time = self._add_time_offset(base_time, duration_offset * (i - 1))
            end_time = self._add_time_offset(start_time, duration_offset)
            
            entry = SubtitleEntry(
                index=i,
                start_time=start_time,
                end_time=end_time,
                text=text
            )
            entries.append(entry)
        
        return SubtitleFile(entries=entries)
    
    def _add_time_offset(self, time_str: str, offset_seconds: float) -> str:
        """Add time offset to SRT time string."""
        try:
            # Parse SRT time format: "00:01:23,456"
            time_part, ms_part = time_str.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            
            # Convert to total milliseconds
            total_ms = (h * 3600 + m * 60 + s) * 1000 + ms
            
            # Add offset
            total_ms += int(offset_seconds * 1000)
            
            # Convert back to SRT format
            hours = total_ms // (3600 * 1000)
            minutes = (total_ms % (3600 * 1000)) // (60 * 1000)
            seconds = (total_ms % (60 * 1000)) // 1000
            milliseconds = total_ms % 1000
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
            
        except (ValueError, IndexError):
            return time_str  # Return original if parsing fails


# Convenience functions
def parse_srt_file(file_path: Union[str, Path]) -> SubtitleFile:
    """
    Convenience function to parse SRT file.
    
    Args:
        file_path: Path to SRT file
        
    Returns:
        Parsed subtitle file
    """
    parser = SRTParser()
    return parser.parse(Path(file_path))


def save_srt_file(subtitle_file: SubtitleFile, output_path: Union[str, Path],
                  use_translation: bool = True):
    """
    Convenience function to save SRT file.
    
    Args:
        subtitle_file: Subtitle file to save
        output_path: Output path
        use_translation: Whether to use translated text
    """
    parser = SRTParser()
    parser.save(subtitle_file, Path(output_path), use_translation)


def create_sample_subtitles() -> SubtitleFile:
    """Create a sample subtitle file for testing."""
    entries = [
        SubtitleEntry(1, "00:00:01,000", "00:00:03,000", "Hello, world!"),
        SubtitleEntry(2, "00:00:04,000", "00:00:06,000", "How are you today?"),
        SubtitleEntry(3, "00:00:07,000", "00:00:09,000", "Welcome to the show."),
        SubtitleEntry(4, "00:00:10,000", "00:00:12,000", "Thank you for watching."),
        SubtitleEntry(5, "00:00:13,000", "00:00:15,000", "See you next time!")
    ]
    
    return SubtitleFile(
        entries=entries,
        source_language=LanguageCode.ENGLISH,
        format_type="srt"
    )
