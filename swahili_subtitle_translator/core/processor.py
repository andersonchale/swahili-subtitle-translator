"""
Subtitle File Processor

Handles loading, processing, and saving of subtitle files in multiple formats.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import re

try:
    import pysrt
except ImportError:
    pysrt = None

try:
    import ass
except ImportError:
    ass = None

from ..utils.formats import SupportedFormats, detect_subtitle_format
from ..utils.exceptions import UnsupportedFormatError, SubtitleProcessingError
from .translator import SubtitleTranslator

logger = logging.getLogger(__name__)


class SubtitleEntry:
    """Represents a single subtitle entry."""
    
    def __init__(
        self,
        start_time: str,
        end_time: str,
        text: str,
        index: int = 0,
        style: Optional[str] = None
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.index = index
        self.style = style
    
    def __repr__(self):
        return f"SubtitleEntry({self.index}: {self.start_time} -> {self.end_time}, '{self.text[:30]}...')"


class SubtitleProcessor:
    """
    Advanced subtitle file processor supporting multiple formats.
    
    Supported formats:
    - SRT (SubRip)
    - ASS/SSA (Advanced SubStation Alpha)
    - VTT (WebVTT)
    - SUB (MicroDVD)
    """
    
    def __init__(self, translator: Optional[SubtitleTranslator] = None):
        """
        Initialize subtitle processor.
        
        Args:
            translator: Optional subtitle translator instance
        """
        self.translator = translator or SubtitleTranslator()
        self.supported_formats = SupportedFormats()
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Validate required dependencies are installed."""
        missing = []
        if pysrt is None:
            missing.append("pysrt")
        
        if missing:
            logger.warning(f"Missing optional dependencies: {missing}")
            logger.warning("Some subtitle formats may not be supported")
    
    def load_subtitle_file(self, file_path: Path) -> List[SubtitleEntry]:
        """
        Load subtitle file and return list of subtitle entries.
        
        Args:
            file_path: Path to subtitle file
            
        Returns:
            List of SubtitleEntry objects
            
        Raises:
            UnsupportedFormatError: If file format is not supported
            SubtitleProcessingError: If file cannot be processed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Subtitle file not found: {file_path}")
        
        # Detect format
        file_format = detect_subtitle_format(file_path)
        logger.info(f"Detected subtitle format: {file_format}")
        
        # Load based on format
        if file_format == 'srt':
            return self._load_srt(file_path)
        elif file_format in ['ass', 'ssa']:
            return self._load_ass(file_path)
        elif file_format == 'vtt':
            return self._load_vtt(file_path)
        elif file_format == 'sub':
            return self._load_sub(file_path)
        else:
            raise UnsupportedFormatError(f"Unsupported subtitle format: {file_format}")
    
    def _load_srt(self, file_path: Path) -> List[SubtitleEntry]:
        """Load SRT subtitle file."""
        if pysrt is None:
            raise SubtitleProcessingError("pysrt is required for SRT support")
        
        try:
            subs = pysrt.open(str(file_path))
            entries = []
            
            for sub in subs:
                entry = SubtitleEntry(
                    start_time=str(sub.start),
                    end_time=str(sub.end),
                    text=sub.text,
                    index=sub.index
                )
                entries.append(entry)
            
            logger.info(f"Loaded {len(entries)} SRT subtitle entries")
            return entries
            
        except Exception as e:
            raise SubtitleProcessingError(f"Failed to load SRT file: {e}")
    
    def _load_ass(self, file_path: Path) -> List[SubtitleEntry]:
        """Load ASS/SSA subtitle file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic ASS parsing (simplified)
            entries = []
            dialogue_pattern = r'Dialogue: \d+,([\d:.,]+),([\d:.,]+),[^,]*,[^,]*,\d+,\d+,\d+,[^,]*,(.*)'
            
            for i, match in enumerate(re.finditer(dialogue_pattern, content)):
                start_time, end_time, text = match.groups()
                
                # Clean ASS formatting tags
                clean_text = re.sub(r'\{[^}]*\}', '', text)
                clean_text = clean_text.replace('\\N', '\n')
                
                entry = SubtitleEntry(
                    start_time=start_time,
                    end_time=end_time,
                    text=clean_text,
                    index=i + 1
                )
                entries.append(entry)
            
            logger.info(f"Loaded {len(entries)} ASS subtitle entries")
            return entries
            
        except Exception as e:
            raise SubtitleProcessingError(f"Failed to load ASS file: {e}")
    
    def _load_vtt(self, file_path: Path) -> List[SubtitleEntry]:
        """Load WebVTT subtitle file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entries = []
            vtt_pattern = r'([\d:.,]+)\s+-->\s+([\d:.,]+)\n(.*?)(?=\n\n|\Z)'
            
            for i, match in enumerate(re.finditer(vtt_pattern, content, re.DOTALL)):
                start_time, end_time, text = match.groups()
                
                # Clean VTT formatting
                clean_text = re.sub(r'<[^>]*>', '', text.strip())
                
                entry = SubtitleEntry(
                    start_time=start_time,
                    end_time=end_time,
                    text=clean_text,
                    index=i + 1
                )
                entries.append(entry)
            
            logger.info(f"Loaded {len(entries)} VTT subtitle entries")
            return entries
            
        except Exception as e:
            raise SubtitleProcessingError(f"Failed to load VTT file: {e}")
    
    def _load_sub(self, file_path: Path) -> List[SubtitleEntry]:
        """Load SUB (MicroDVD) subtitle file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            entries = []
            fps = 25  # Default FPS, should be detected from file
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # MicroDVD format: {start}{end}text
                match = re.match(r'\{(\d+)\}\{(\d+)\}(.*)', line)
                if match:
                    start_frame, end_frame, text = match.groups()
                    
                    # Convert frames to time (assuming 25fps)
                    start_time = self._frames_to_time(int(start_frame), fps)
                    end_time = self._frames_to_time(int(end_frame), fps)
                    
                    entry = SubtitleEntry(
                        start_time=start_time,
                        end_time=end_time,
                        text=text,
                        index=i + 1
                    )
                    entries.append(entry)
            
            logger.info(f"Loaded {len(entries)} SUB subtitle entries")
            return entries
            
        except Exception as e:
            raise SubtitleProcessingError(f"Failed to load SUB file: {e}")
    
    def _frames_to_time(self, frame: int, fps: int) -> str:
        """Convert frame number to time string."""
        total_seconds = frame / fps
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    
    def save_subtitle_file(
        self,
        entries: List[SubtitleEntry],
        output_path: Path,
        format_type: str = 'srt'
    ):
        """
        Save subtitle entries to file.
        
        Args:
            entries: List of subtitle entries
            output_path: Output file path
            format_type: Output format ('srt', 'vtt', etc.)
        """
        if format_type == 'srt':
            self._save_srt(entries, output_path)
        elif format_type == 'vtt':
            self._save_vtt(entries, output_path)
        else:
            raise UnsupportedFormatError(f"Saving in {format_type} format not supported")
    
    def _save_srt(self, entries: List[SubtitleEntry], output_path: Path):
        """Save entries as SRT format."""
        if pysrt is None:
            # Fallback to manual SRT writing
            self._save_srt_manual(entries, output_path)
            return
        
        try:
            subs = pysrt.SubRipFile()
            
            for entry in entries:
                sub = pysrt.SubRipItem()
                sub.index = entry.index
                sub.start = pysrt.SubRipTime.from_ordinal(self._time_to_ordinal(entry.start_time))
                sub.end = pysrt.SubRipTime.from_ordinal(self._time_to_ordinal(entry.end_time))
                sub.text = entry.text
                subs.append(sub)
            
            subs.save(str(output_path))
            logger.info(f"Saved {len(entries)} subtitles to {output_path}")
            
        except Exception as e:
            logger.warning(f"pysrt save failed, using manual method: {e}")
            self._save_srt_manual(entries, output_path)
    
    def _save_srt_manual(self, entries: List[SubtitleEntry], output_path: Path):
        """Manually save SRT format without pysrt."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    f.write(f"{entry.index}\n")
                    f.write(f"{entry.start_time} --> {entry.end_time}\n")
                    f.write(f"{entry.text}\n\n")
            
            logger.info(f"Manually saved {len(entries)} subtitles to {output_path}")
            
        except Exception as e:
            raise SubtitleProcessingError(f"Failed to save SRT file: {e}")
    
    def _save_vtt(self, entries: List[SubtitleEntry], output_path: Path):
        """Save entries as WebVTT format."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                
                for entry in entries:
                    f.write(f"{entry.start_time} --> {entry.end_time}\n")
                    f.write(f"{entry.text}\n\n")
            
            logger.info(f"Saved {len(entries)} subtitles to VTT: {output_path}")
            
        except Exception as e:
            raise SubtitleProcessingError(f"Failed to save VTT file: {e}")
    
    def _time_to_ordinal(self, time_str: str) -> int:
        """Convert time string to ordinal (milliseconds)."""
        # Simple conversion for SRT time format
        try:
            parts = time_str.replace(',', '.').split(':')
            if len(parts) == 3:
                hours, minutes, seconds = parts
                total_ms = (int(hours) * 3600 + int(minutes) * 60 + float(seconds)) * 1000
                return int(total_ms)
        except:
            pass
        return 0
    
    def translate_subtitles(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        progress_callback=None
    ) -> Path:
        """
        Translate subtitle file from English to Swahili.
        
        Args:
            input_path: Input subtitle file path
            output_path: Output subtitle file path (auto-generated if None)
            progress_callback: Progress callback function
            
        Returns:
            Path to translated subtitle file
        """
        # Generate output path if not provided
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_swahili{input_path.suffix}"
        
        logger.info(f"Translating subtitles: {input_path} -> {output_path}")
        
        # Load subtitle file
        entries = self.load_subtitle_file(input_path)
        
        # Extract texts for translation
        texts = [entry.text for entry in entries]
        
        # Translate texts
        def translation_progress(current, total):
            if progress_callback:
                progress = (current / total) * 100
                progress_callback(f"Translating: {current}/{total} ({progress:.1f}%)")
        
        translated_texts = self.translator.translate_batch(texts, translation_progress)
        
        # Update entries with translated texts
        for entry, translated_text in zip(entries, translated_texts):
            entry.text = translated_text
        
        # Determine output format
        output_format = detect_subtitle_format(output_path)
        
        # Save translated subtitles
        self.save_subtitle_file(entries, output_path, output_format)
        
        logger.info(f"Translation completed: {output_path}")
        return output_path
    
    def batch_translate(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        file_pattern: str = "*.srt",
        progress_callback=None
    ) -> List[Path]:
        """
        Translate all subtitle files in a directory.
        
        Args:
            input_dir: Input directory containing subtitle files
            output_dir: Output directory (created if doesn't exist)
            file_pattern: File pattern to match (e.g., "*.srt", "*.ass")
            progress_callback: Progress callback function
            
        Returns:
            List of paths to translated files
        """
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Create output directory
        if output_dir is None:
            output_dir = input_dir / "translated_swahili"
        
        output_dir.mkdir(exist_ok=True)
        
        # Find subtitle files
        subtitle_files = list(input_dir.glob(file_pattern))
        if not subtitle_files:
            logger.warning(f"No subtitle files found matching pattern: {file_pattern}")
            return []
        
        logger.info(f"Found {len(subtitle_files)} subtitle files to translate")
        
        translated_files = []
        
        for i, subtitle_file in enumerate(subtitle_files):
            try:
                # Generate output filename
                output_file = output_dir / f"{subtitle_file.stem}_swahili{subtitle_file.suffix}"
                
                # Progress callback for overall batch progress
                def batch_progress(message):
                    if progress_callback:
                        overall_progress = f"File {i+1}/{len(subtitle_files)}: {message}"
                        progress_callback(overall_progress)
                
                # Translate file
                result_path = self.translate_subtitles(subtitle_file, output_file, batch_progress)
                translated_files.append(result_path)
                
                logger.info(f"Completed translation: {subtitle_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to translate {subtitle_file}: {e}")
                continue
        
        logger.info(f"Batch translation completed: {len(translated_files)} files translated")
        return translated_files
    
    def get_subtitle_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get information about a subtitle file.
        
        Args:
            file_path: Path to subtitle file
            
        Returns:
            Dictionary containing file information
        """
        try:
            entries = self.load_subtitle_file(file_path)
            
            total_duration = 0
            if entries:
                # Calculate total duration (simplified)
                last_entry = entries[-1]
                # This is a simplified calculation
                total_duration = "Unknown"
            
            info = {
                'file_path': str(file_path),
                'format': detect_subtitle_format(file_path),
                'total_entries': len(entries),
                'total_duration': total_duration,
                'file_size': file_path.stat().st_size if file_path.exists() else 0,
                'encoding': 'utf-8'  # Assumed
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get subtitle info: {e}")
            return {
                'file_path': str(file_path),
                'error': str(e)
            }
