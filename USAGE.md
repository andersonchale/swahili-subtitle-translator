# Swahili Subtitle Translator - Usage Guide

This comprehensive guide covers all aspects of using the Swahili Subtitle Translator, from basic commands to advanced configuration and API usage.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Command Reference](#command-reference)
4. [Configuration](#configuration)
5. [Translation Services](#translation-services)
6. [Subtitle Sources](#subtitle-sources)
7. [API Usage](#api-usage)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Features](#advanced-features)

## Installation

### Quick Install

```bash
git clone https://github.com/andersonchale/swahili-subtitle-translator.git
cd swahili-subtitle-translator
pip install -r requirements.txt
```

### Development Install

```bash
pip install -e .
```

This creates the `swahili-translator` command globally.

### Module Usage (No Install)

You can also run directly without installation:

```bash
python -m swahili_subtitle_translator --help
```

## Basic Usage

### Search for Subtitles

```bash
# Basic search
swahili-translator search "The Matrix"

# Search with filters
swahili-translator search "Avatar" --year 2009 --limit 5

# Search and download
swahili-translator search "Inception" --download --output ./downloads
```

### Translate Subtitles

```bash
# Basic translation
swahili-translator translate movie.srt

# With specific service
swahili-translator translate movie.srt --service google_translate

# Custom output file
swahili-translator translate movie.srt --output movie_swahili.srt
```

### Complete Pipeline

```bash
# Search, download, and translate in one command
swahili-translator pipeline "The Lion King" --target-language sw

# Advanced pipeline
swahili-translator pipeline "Breaking Bad" --season 1 --episode 1 --cleanup
```

## Command Reference

### Global Options

| Option | Description |
|--------|-------------|
| `--config` | Specify configuration file path |
| `--debug` | Enable debug logging |
| `--verbose` | Show detailed output |
| `--no-color` | Disable colored output |

### Search Command

```bash
swahili-translator search TITLE [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--language, -l` | Source language (default: en) |
| `--year, -y` | Release year |
| `--season, -s` | TV show season |
| `--episode, -e` | TV show episode |
| `--limit` | Maximum results |
| `--sources` | Sources to search (opensubtitles, subscene, yify) |
| `--download, -d` | Download subtitles |
| `--output, -o` | Output directory |

### Translate Command

```bash
swahili-translator translate INPUT [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--output, -o` | Output file path |
| `--service` | Translation service (google_translate, openai_gpt, mock) |
| `--target-language, -t` | Target language (default: sw) |
| `--no-validate` | Skip validation |

### Pipeline Command

```bash
swahili-translator pipeline TITLE [OPTIONS]
```

Combines search, download, and translate operations.

### Config Command

```bash
swahili-translator config ACTION [OPTIONS]
```

| Action | Description |
|--------|-------------|
| `show` | Display current configuration |
| `create` | Create sample configuration file |
| `validate` | Validate configuration |

### Test Command

```bash
swahili-translator test
```

Tests all configured services to verify they're working.

## Configuration

### Configuration File

Create `swahili_translator_config.json`:

```json
{
  "debug": false,
  "verbose": false,
  "log_level": "INFO",
  "default_source_language": "en",
  "default_target_language": "sw",
  "show_progress": true,
  "colored_output": true,
  
  "translation": {
    "google_api_key": null,
    "openai_api_key": null,
    "default_service": "mock",
    "fallback_services": ["offline_model", "mock"],
    "quality_threshold": 0.6,
    "max_retries": 3,
    "batch_size": 100,
    "parallel_processing": true,
    "rate_limit": 1.0
  },
  
  "search": {
    "default_sources": ["opensubtitles", "subscene", "yify"],
    "max_results": 10,
    "timeout": 30,
    "download_directory": "./downloads",
    "overwrite_existing": false,
    "opensubtitles_api_key": null
  }
}
```

### Environment Variables

```bash
# Translation services
export GOOGLE_TRANSLATE_API_KEY="your-google-api-key"
export OPENAI_API_KEY="your-openai-api-key"

# Search services
export OPENSUBTITLES_API_KEY="your-opensubtitles-api-key"

# General settings
export SWAHILI_TRANSLATOR_DEBUG="true"
export DOWNLOAD_DIR="./my_downloads"
```

## Translation Services

### Google Translate

**Setup:**
1. Get Google Cloud Translation API key
2. Set environment variable or add to config file

**Features:**
- High accuracy (85-90%)
- Fast translation
- Cost per character
- 100+ languages supported

**Cost:** ~$20 per 1M characters

### OpenAI GPT

**Setup:**
1. Get OpenAI API key
2. Set environment variable or add to config file

**Features:**
- Context-aware translation
- Cultural understanding
- Custom prompts for movies
- Higher quality for complex content

**Cost:** ~$2-3 per 1K tokens

### Mock Service

**Features:**
- Free testing service
- No API key required
- Predefined translations for common phrases
- Fallback for development

### Offline Models

**Setup:**
1. Install transformers: `pip install transformers torch`
2. Download models (requires ~1-5GB storage)

**Features:**
- No API costs after setup
- Privacy-friendly
- Works offline
- Requires significant storage

## Subtitle Sources

### OpenSubtitles

- **Database:** Millions of subtitles
- **Languages:** 60+ languages
- **Quality:** Community-driven
- **API:** Optional API key for better limits

### Subscene

- **Database:** Curated high-quality subtitles
- **Languages:** Major languages
- **Quality:** Manually reviewed
- **API:** Web scraping (no API)

### YIFY Subtitles

- **Database:** Movie-focused
- **Languages:** Popular languages
- **Quality:** Clean, consistent
- **API:** Web scraping

## API Usage

### Python API

```python
from swahili_subtitle_translator.search import SubtitleSearchEngine, SearchQuery
from swahili_subtitle_translator.translation import create_translation_engine

# Search for subtitles
engine = SubtitleSearchEngine()
query = SearchQuery(title="The Matrix", year=1999)
results = engine.search(query)

# Translate subtitle file
translator = create_translation_engine(google_api_key="your-key")
translated_file = translator.translate_subtitle_file(subtitle_file)
```

### Search API

```python
from swahili_subtitle_translator.search import search_subtitles

# Simple search
results = search_subtitles("Inception", limit=5)
for result in results:
    print(f"Found: {result.display_name}")
```

### Translation API

```python
from swahili_subtitle_translator.translation import translate_simple

# Simple translation
translated = translate_simple("Hello world", target_language="sw")
print(translated)  # Output: "Hujambo dunia"
```

## Troubleshooting

### Common Issues

**1. Command not found**
```bash
# Use module syntax instead
python -m swahili_subtitle_translator --help
```

**2. Import errors**
```bash
# Install dependencies
pip install -r requirements.txt
```

**3. Translation service errors**
```bash
# Test services
swahili-translator test

# Try different service
swahili-translator translate movie.srt --service mock
```

**4. No search results**
```bash
# Try different sources
swahili-translator search "Movie" --sources opensubtitles

# Check spelling and try variations
swahili-translator search "Matrix" --year 1999
```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
swahili-translator --debug --verbose search "Movie"
```

### Log Files

Configure log files in the configuration:

```json
{
  "log_file": "./swahili_translator.log"
}
```

## Advanced Features

### Batch Processing

```bash
# Process multiple files
for file in *.srt; do
  swahili-translator translate "$file"
done
```

### Custom Prompts (OpenAI)

The OpenAI service uses context-aware prompts optimized for subtitle content.

### Quality Thresholds

Set minimum translation quality:

```json
{
  "translation": {
    "quality_threshold": 0.8
  }
}
```

### Fallback Chains

Configure service fallbacks:

```json
{
  "translation": {
    "default_service": "google_translate",
    "fallback_services": ["openai_gpt", "mock"]
  }
}
```

### Progress Callbacks

```python
def progress_callback(completed, total):
    print(f"Progress: {completed}/{total}")

engine.translate_subtitle_file(subtitle_file, progress_callback=progress_callback)
```

### Custom Configuration Locations

```bash
# Use custom config file
swahili-translator --config ./my_config.json search "Movie"
```

### Validation

```bash
# Skip validation for faster processing
swahili-translator translate movie.srt --no-validate

# Validate configuration
swahili-translator config validate
```

## Performance Tips

1. **Use caching:** Results are cached to avoid repeated API calls
2. **Batch processing:** Process multiple files together
3. **Quality thresholds:** Set appropriate quality levels
4. **Rate limiting:** Configure appropriate delays
5. **Parallel processing:** Enable for faster translation

## Integration Examples

### Shell Script

```bash
#!/bin/bash
# Batch translate all SRT files in a directory

for file in *.srt; do
    echo "Translating: $file"
    swahili-translator translate "$file" --service google_translate
done
```

### Python Script

```python
#!/usr/bin/env python3
import os
from pathlib import Path
from swahili_subtitle_translator.translation import create_translation_engine

# Setup
engine = create_translation_engine(google_api_key=os.getenv('GOOGLE_API_KEY'))

# Process all SRT files
for srt_file in Path('.').glob('*.srt'):
    print(f"Translating: {srt_file}")
    translated = engine.translate_subtitle_file(srt_file)
    output_path = srt_file.with_suffix('.sw.srt')
    translated.save(output_path)
```

## Best Practices

1. **Always test services first:** `swahili-translator test`
2. **Use appropriate quality thresholds:** 0.6-0.8 for most content
3. **Review translations:** Especially for professional content
4. **Configure fallbacks:** Have backup translation services
5. **Monitor costs:** Track API usage for paid services
6. **Use caching:** Avoid redundant translations
7. **Validate input:** Check subtitle files before processing

---

For more information, see the [README.md](README.md) or check the inline help:

```bash
swahili-translator --help
swahili-translator search --help
swahili-translator translate --help
```
