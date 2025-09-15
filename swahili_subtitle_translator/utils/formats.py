"""
Subtitle format detection and handling utilities.
"""

from pathlib import Path
from typing import List, Dict, Any
import re


class SupportedFormats:
    """Container for supported subtitle formats."""
    
    # Supported subtitle formats
    FORMATS = {
        'srt': {
            'name': 'SubRip',
            'extensions': ['.srt'],
            'description': 'SubRip subtitle format',
            'read': True,
            'write': True
        },
        'ass': {
            'name': 'Advanced SubStation Alpha',
            'extensions': ['.ass'],
            'description': 'Advanced SubStation Alpha format',
            'read': True,
            'write': False
        },
        'ssa': {
            'name': 'SubStation Alpha',
            'extensions': ['.ssa'],
            'description': 'SubStation Alpha format',
            'read': True,
            'write': False
        },
        'vtt': {
            'name': 'WebVTT',
            'extensions': ['.vtt'],
            'description': 'WebVTT subtitle format',
            'read': True,
            'write': True
        },
        'sub': {
            'name': 'MicroDVD',
            'extensions': ['.sub'],
            'description': 'MicroDVD subtitle format',
            'read': True,
            'write': False
        }
    }
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get list of supported format names."""
        return list(cls.FORMATS.keys())
    
    @classmethod
    def get_readable_formats(cls) -> List[str]:
        """Get list of readable format names."""
        return [fmt for fmt, info in cls.FORMATS.items() if info['read']]
    
    @classmethod
    def get_writable_formats(cls) -> List[str]:
        """Get list of writable format names."""
        return [fmt for fmt, info in cls.FORMATS.items() if info['write']]
    
    @classmethod
    def get_extensions(cls) -> List[str]:
        """Get list of all supported extensions."""
        extensions = []
        for info in cls.FORMATS.values():
            extensions.extend(info['extensions'])
        return extensions
    
    @classmethod
    def get_format_info(cls, format_name: str) -> Dict[str, Any]:
        """Get information about a specific format."""
        return cls.FORMATS.get(format_name, {})


def detect_subtitle_format(file_path: Path) -> str:
    """
    Detect subtitle format based on file extension and content.
    
    Args:
        file_path: Path to subtitle file
        
    Returns:
        Format name (e.g., 'srt', 'ass', 'vtt')
        
    Raises:
        ValueError: If format cannot be detected
    """
    # First, try to detect by extension
    extension = file_path.suffix.lower()
    
    for format_name, info in SupportedFormats.FORMATS.items():
        if extension in info['extensions']:
            return format_name
    
    # If extension detection fails, try content-based detection
    if file_path.exists():
        return _detect_format_by_content(file_path)
    
    raise ValueError(f"Cannot detect subtitle format for: {file_path}")


def _detect_format_by_content(file_path: Path) -> str:
    """
    Detect subtitle format by analyzing file content.
    
    Args:
        file_path: Path to subtitle file
        
    Returns:
        Format name
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1024)  # Read first 1KB
        
        # Check for SRT format (numeric index + timestamp)
        srt_pattern = r'^\d+\s*\n\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}'
        if re.search(srt_pattern, content, re.MULTILINE):
            return 'srt'
        
        # Check for WebVTT format
        if content.startswith('WEBVTT'):
            return 'vtt'
        
        # Check for ASS/SSA format
        if '[Script Info]' in content and 'Dialogue:' in content:
            return 'ass'
        
        # Check for MicroDVD format
        if re.search(r'^\{\d+\}\{\d+\}', content):
            return 'sub'
        
        # Default to SRT if no other format detected
        return 'srt'
        
    except Exception:
        # If content detection fails, default to SRT
        return 'srt'


def is_supported_format(file_path: Path) -> bool:
    """
    Check if file format is supported.
    
    Args:
        file_path: Path to subtitle file
        
    Returns:
        True if format is supported, False otherwise
    """
    try:
        detect_subtitle_format(file_path)
        return True
    except ValueError:
        return False


def get_output_extension(input_path: Path, output_format: str = 'srt') -> str:
    """
    Get appropriate output extension for given format.
    
    Args:
        input_path: Input file path
        output_format: Desired output format
        
    Returns:
        File extension (e.g., '.srt', '.vtt')
    """
    format_info = SupportedFormats.get_format_info(output_format)
    if format_info and format_info['extensions']:
        return format_info['extensions'][0]
    
    # Default to input extension if output format not found
    return input_path.suffix


def validate_subtitle_file(file_path: Path) -> Dict[str, Any]:
    """
    Validate subtitle file and return information about it.
    
    Args:
        file_path: Path to subtitle file
        
    Returns:
        Dictionary containing validation results
    """
    result = {
        'valid': False,
        'format': None,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    try:
        # Check if file exists
        if not file_path.exists():
            result['errors'].append(f"File does not exist: {file_path}")
            return result
        
        # Check if file is readable
        if not file_path.is_file():
            result['errors'].append(f"Path is not a file: {file_path}")
            return result
        
        # Detect format
        try:
            format_name = detect_subtitle_format(file_path)
            result['format'] = format_name
            result['info']['detected_format'] = format_name
        except ValueError as e:
            result['errors'].append(f"Cannot detect format: {e}")
            return result
        
        # Check file size
        file_size = file_path.stat().st_size
        result['info']['file_size'] = file_size
        
        if file_size == 0:
            result['errors'].append("File is empty")
            return result
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            result['warnings'].append("File is very large (>10MB)")
        
        # Basic content validation
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 chars
            
            result['info']['encoding'] = 'utf-8'
            
            # Check for common issues
            if not content.strip():
                result['errors'].append("File appears to be empty or contains only whitespace")
                return result
            
            # Format-specific validation
            if format_name == 'srt':
                if not re.search(r'\d+\s*\n.*-->', content):
                    result['warnings'].append("SRT format validation failed - may not be valid SRT")
            
            elif format_name == 'vtt':
                if not content.startswith('WEBVTT'):
                    result['warnings'].append("WebVTT file should start with 'WEBVTT'")
        
        except UnicodeDecodeError:
            result['warnings'].append("File encoding may not be UTF-8")
            result['info']['encoding'] = 'unknown'
        
        # If we got here, file is considered valid
        result['valid'] = True
        
    except Exception as e:
        result['errors'].append(f"Validation failed: {e}")
    
    return result
