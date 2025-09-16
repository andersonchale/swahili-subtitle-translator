# 🎬 Swahili Subtitle Translator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A professional, open-source tool for translating subtitle files from English to Swahili. Perfect for content creators, translators, and media enthusiasts who want to make English content accessible to Swahili speakers.

## ✨ Features

- **🌍 Multiple Translation Services**: Google Translate and MyMemory support with automatic fallback
- **📁 Multiple Subtitle Formats**: SRT, ASS/SSA, VTT, and SUB format support  
- **⚡ Smart Caching**: SQLite-based translation cache to reduce API calls and improve speed
- **🔄 Batch Processing**: Translate entire directories of subtitle files
- **🎯 Cultural Adaptation**: Built-in Swahili cultural context and common phrase translations
- **🛡️ Robust Error Handling**: Automatic retry mechanism and graceful failure handling
- **📊 Progress Tracking**: Real-time progress bars and detailed statistics
- **🎨 Beautiful CLI**: Colorized command-line interface with professional output
- **🔧 Highly Configurable**: Extensive customization options and settings

## 🚀 Quick Start

### Method 1: Global Installation (Recommended)

**🎯 One-Command Installation:**

```bash
# Clone the repository
git clone https://github.com/andersonchale/swahili-subtitle-translator.git
cd swahili-subtitle-translator

# Run the automated installation script
chmod +x install_global.sh
./install_global.sh
```

This script will:
- Detect your operating system (Linux/macOS/Windows Git Bash)
- Offer installation options (system-wide, user, virtual environment, or pipx)
- Handle modern Python restrictions (PEP 668 externally-managed environments)
- Make `sst` and `swahili-sub-translate` commands globally available
- Test the installation automatically

**🌐 Manual Global Installation:**

```bash
# Method A: pipx (recommended for modern Python - handles PEP 668)
sudo apt install pipx  # Ubuntu/Debian
# brew install pipx   # macOS
pipx install /path/to/swahili-subtitle-translator

# Method B: User installation (no admin rights needed)
pip3 install --user /path/to/swahili-subtitle-translator

# Add ~/.local/bin to PATH if needed (Linux/macOS)
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc

# Method C: System-wide (may fail on modern Ubuntu/Debian due to PEP 668)
sudo pip3 install /path/to/swahili-subtitle-translator
# If it fails: sudo pip3 install --break-system-packages /path/to/swahili-subtitle-translator

# Refresh command cache
hash -r
```

**✅ Test Global Installation:**
```bash
# Test from any directory
cd ~/Desktop
sst --help
swahili-sub-translate --help

# These should work from anywhere!
sst search "The Matrix" --limit 3
sst pipeline "Inception" --output inception_swahili.srt
```

### Method 2: Virtual Environment (Development)

```bash
git clone https://github.com/andersonchale/swahili-subtitle-translator.git
cd swahili-subtitle-translator

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows Git Bash: source .venv/Scripts/activate

# Install in editable mode
pip install -e .

# Commands available while venv is active
sst --help
swahili-sub-translate --help
```

### Method 3: Direct Python Usage (No Installation)

```bash
# Clone and use directly
git clone https://github.com/andersonchale/swahili-subtitle-translator.git
cd swahili-subtitle-translator
pip3 install -r requirements.txt

# Use with Python module syntax
python3 -m swahili_subtitle_translator search "The Matrix"
python3 -m swahili_subtitle_translator pipeline "Inception" -o output.srt
```

### Method 4: Install from PyPI (Future)

```bash
# When published to PyPI
pip3 install swahili-subtitle-translator
sst --help  # Available globally
```

### Basic Usage Examples

```bash
# Method 1 (Direct Python usage)
python3 -m swahili_subtitle_translator.cli.main movie.srt
python3 -m swahili_subtitle_translator.cli.main movie.srt -o movie_swahili.srt
python3 -m swahili_subtitle_translator.cli.main /path/to/subtitles --batch

# Method 2 (After pip install -e .)
swahili-sub-translate movie.srt
swahili-sub-translate movie.srt --service mymemory
swahili-sub-translate movie.srt --stats
```

## 📖 Detailed Usage

### Single File Translation

**Method 1 (Direct Python - No installation needed):**
```bash
# Basic translation
python3 -m swahili_subtitle_translator.cli.main "Game of Thrones S01E01.srt"

# With custom output path
python3 -m swahili_subtitle_translator.cli.main "movie.srt" -o "output/movie_swahili.srt"

# With specific translation service
python3 -m swahili_subtitle_translator.cli.main "movie.srt" --service mymemory --stats
```

**Method 2 (After `pip install -e .`):**
```bash
# Basic translation
swahili-sub-translate "Game of Thrones S01E01.srt"

# With custom output path
swahili-sub-translate "movie.srt" -o "output/movie_swahili.srt"

# With specific translation service
swahili-sub-translate "movie.srt" --service mymemory --stats
```

### Batch Translation

**Method 1 (Direct Python):**
```bash
# Translate all .srt files in a directory
python3 -m swahili_subtitle_translator.cli.main /movies/subtitles --batch

# Translate specific patterns
python3 -m swahili_subtitle_translator.cli.main /movies --batch --pattern "*.srt" --pattern "*.ass"

# Custom output directory
python3 -m swahili_subtitle_translator.cli.main /input --batch -o /output/swahili
```

**Method 2 (After installation):**
```bash
# Translate all .srt files in a directory
swahili-sub-translate /movies/subtitles --batch

# Translate specific patterns
swahili-sub-translate /movies --batch --pattern "*.srt" --pattern "*.ass"

# Custom output directory
swahili-sub-translate /input --batch -o /output/swahili
```

### Advanced Options

```bash
# Method 1 (Direct Python)
python3 -m swahili_subtitle_translator.cli.main movie.srt --no-cache
python3 -m swahili_subtitle_translator.cli.main movie.srt --max-retries 5
python3 -m swahili_subtitle_translator.cli.main movie.srt --verbose
python3 -m swahili_subtitle_translator.cli.main movie.srt --quiet

# Method 2 (After installation)
swahili-sub-translate movie.srt --no-cache
swahili-sub-translate movie.srt --max-retries 5
swahili-sub-translate movie.srt --verbose
swahili-sub-translate movie.srt --quiet
```

### Information and Management

```bash
# Method 1 (Direct Python)
python3 -m swahili_subtitle_translator.cli.main --info --formats
python3 -m swahili_subtitle_translator.cli.main --info --file movie.srt
python3 -m swahili_subtitle_translator.cli.main --cache --cache-stats
python3 -m swahili_subtitle_translator.cli.main --cache --clear-cache

# Method 2 (After installation)
swahili-sub-translate --info --formats
swahili-sub-translate --info --file movie.srt
swahili-sub-translate --cache --cache-stats
swahili-sub-translate --cache --clear-cache
```

## 🎬 Subtitle Search & Pipeline Features

In addition to translating existing subtitle files, this tool now supports searching for subtitles from multiple sources and performing complete search-download-translate workflows.

### Searching for Subtitles

Use the `search` command to find subtitles for movies or TV shows:

```bash
# Method 1 (Direct Python)
python3 -m swahili_subtitle_translator.cli.main search "Movie Title" --limit 3
python3 -m swahili_subtitle_translator.cli.main search "Game of Thrones" --season 1 --episode 1

# Method 2 (After installation)
sst search "Movie Title" --limit 3
sst search "Game of Thrones" --season 1 --episode 1 --year 2011
```

**Search Options:**
- `--limit`: Maximum number of results to return (default: 5)
- `--year`: Movie release year or TV show year
- `--season`: TV show season number
- `--episode`: TV show episode number
- `--sources`: Limit search to specific sources (e.g., `opensubtitles`, `subscene`, `yify`, `mock`)

### Using the Complete Pipeline

The `pipeline` command performs the full workflow of searching, downloading, and translating subtitles automatically:

```bash
# Method 1 (Direct Python)
# Basic pipeline usage
python3 -m swahili_subtitle_translator.cli.main pipeline "Inception" --limit 1 --output inception_swahili.srt

# With specific options
python3 -m swahili_subtitle_translator.cli.main pipeline "Breaking Bad" \
    --season 1 --episode 1 \
    --output breaking_bad_s01e01_swahili.srt \
    --service google \
    --target-language sw

# Method 2 (After installation)
# Basic pipeline usage
sst pipeline "Inception" --limit 1 --output inception_swahili.srt

# With specific options
sst pipeline "Breaking Bad" \
    --season 1 --episode 1 \
    --output breaking_bad_s01e01_swahili.srt \
    --service google \
    --target-language sw
```

**Pipeline Options:**
- `--output` or `-o`: Path for the translated subtitle file
- `--source-language`: Source subtitle language (default: English)
- `--target-language` or `-t`: Target translation language (default: Swahili)
- `--service`: Translation service (`google`, `mymemory`, `mock`)
- `--year`, `--season`, `--episode`: Media metadata for better search results
- `--limit`: Maximum subtitle search results to consider
- `--sources`: Subtitle sources to search (e.g., `opensubtitles`, `subscene`, `yify`, `mock`)
- `--temp-dir`: Directory for temporary downloaded files
- `--cleanup`: Remove temporary files after processing (default: true)
- `--no-validate`: Skip subtitle validation checks

### Pipeline Workflow

The pipeline command performs these steps automatically:

1. **🔍 Search**: Searches configured subtitle sources for matches
2. **📥 Download**: Downloads the best matching subtitle file
3. **🌍 Translate**: Translates the subtitle from source to target language
4. **💾 Save**: Saves the translated subtitle to the specified output file
5. **🧹 Cleanup**: Removes temporary files (if enabled)

### Subtitle Sources

The tool supports multiple subtitle sources:

- **OpenSubtitles**: Large database of movie and TV subtitles
- **Subscene**: Popular subtitle community site
- **YIFY**: Movie subtitles from YIFY releases
- **Mock**: Test source with demo subtitles (for testing)

**Note**: Real subtitle sources may require API keys and are subject to anti-bot protections. The mock source is perfect for testing the functionality without external dependencies.

### Configuration for Search & Pipeline

For development or updates to the search functionality:

```bash
# Navigate to project directory
cd /home/tekfluent/Projects/swahili-subtitle-translator

# Activate virtual environment
source .venv/bin/activate

# Reinstall with latest changes
pip install -e . --force-reinstall --no-deps

# Test the pipeline
sst pipeline "Test Movie" --sources mock --output test_output.srt
```

### Examples

**Movie Translation Pipeline:**
```bash
# Search and translate a movie subtitle
sst pipeline "The Dark Knight" --year 2008 --output dark_knight_swahili.srt
```

**TV Show Translation Pipeline:**
```bash
# Search and translate a TV show episode
sst pipeline "Friends" --season 1 --episode 1 --year 1994 --output friends_s01e01_swahili.srt
```

**Testing with Mock Source:**
```bash
# Test pipeline functionality without real web scraping
sst pipeline "Test Movie" --sources mock --output test_swahili.srt
```

## 🏗️ Project Structure

```
swahili-subtitle-translator/
├── swahili_subtitle_translator/
│   ├── __init__.py                 # Package initialization
│   ├── core/
│   │   ├── __init__.py
│   │   ├── translator.py           # Translation engine
│   │   └── processor.py            # Subtitle file processor
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py                 # Command-line interface
│   └── utils/
│       ├── __init__.py
│       ├── cache.py                # Translation caching
│       ├── exceptions.py           # Custom exceptions
│       └── formats.py              # Format detection & validation
├── tests/                          # Test suite
├── docs/                           # Documentation
├── examples/                       # Example files and scripts
├── requirements.txt                # Dependencies
├── setup.py                        # Package setup
├── README.md                       # This file
├── LICENSE                         # MIT License
├── CONTRIBUTING.md                 # Contribution guidelines
└── .gitignore                      # Git ignore rules
```

## 🎯 Supported Formats

| Format | Read | Write | Description |
|--------|------|-------|-------------|
| **SRT** | ✅ | ✅ | SubRip - Most common subtitle format |
| **ASS** | ✅ | ❌ | Advanced SubStation Alpha |
| **SSA** | ✅ | ❌ | SubStation Alpha |
| **VTT** | ✅ | ✅ | WebVTT - Web video subtitles |
| **SUB** | ✅ | ❌ | MicroDVD subtitle format |

## 🔧 Configuration

The translator supports various configuration options:

### Translation Services

- **Google Translate** (default): High-quality translations with good Swahili support
- **MyMemory**: Alternative service with fallback capability

### Caching System

- **SQLite-based**: Persistent, efficient caching
- **Automatic cleanup**: Removes old entries to save space
- **Hit rate tracking**: Monitor cache performance

### Cultural Adaptations

The tool includes built-in adaptations for common English phrases to culturally appropriate Swahili:

- "Your Grace" → "Neema yako"
- "My Lord" → "Bwana wangu"
- "Winter is coming" → "Baridi inakuja"
- And many more...

## 🧪 Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/andersonchale/swahili-subtitle-translator.git
cd swahili-subtitle-translator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=swahili_subtitle_translator

# Format code
black .

# Lint code
flake8 swahili_subtitle_translator
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_translator.py

# Run with coverage report
pytest --cov=swahili_subtitle_translator --cov-report=html
```

## 📊 Performance

### Translation Speed
- **Single file**: ~100-500 subtitles per minute
- **Batch processing**: Depends on subtitle count and API limits
- **Cache hits**: Instant (0ms per cached translation)

### Accuracy
- **Google Translate**: ~85-90% accuracy for general content
- **Cultural adaptations**: Custom rules for improved context
- **Manual review recommended**: For professional content

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 Use Cases

### Content Creators
- **YouTube Creators**: Translate English video subtitles to reach Swahili-speaking audiences
- **Educational Content**: Make learning materials accessible
- **Entertainment**: Translate movies, TV shows, and documentaries

### Professional Translators
- **Bulk Translation**: Process large volumes of subtitle files efficiently
- **Quality Assurance**: Use as a first-pass translation for manual refinement
- **Consistency**: Maintain consistent terminology across projects

### Media Companies
- **Localization**: Adapt content for East African markets
- **Cost Efficiency**: Reduce manual translation workload
- **Scalability**: Handle large subtitle libraries

## 🌍 Swahili Language Support

This tool is specifically optimized for English to Swahili translation:

- **Regional Variations**: Supports standard Swahili (Kiswahili sanifu)
- **Cultural Context**: Includes cultural adaptations for better relevance
- **Common Phrases**: Built-in dictionary for frequent expressions
- **Technical Terms**: Handles technical vocabulary appropriately

## 🔐 Privacy & Security

- **No Data Storage**: Translations are cached locally only
- **API Keys**: Use your own translation service credentials
- **Open Source**: Full transparency in how translations are processed

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Internet Connection**: Required for translation services
- **Storage**: Minimal (cache database typically <10MB)

## 🐛 Troubleshooting

### Command Not Found Errors

**Problem**: `sst: command not found` or `swahili-sub-translate: command not found`

**Solutions**:

1. **Refresh command cache** (Most common fix):
   ```bash
   hash -r
   sst --help  # Try again
   ```

2. **Check if commands are installed**:
   ```bash
   # Check if the executables exist
   ls -la ~/.local/bin/ | grep -E "(sst|swahili)"
   # Or for system installation:
   which sst
   which swahili-sub-translate
   ```

3. **Verify PATH includes the installation directory**:
   ```bash
   echo $PATH
   # Should include ~/.local/bin (user install) or /usr/local/bin (system install)
   ```

4. **Add to PATH if missing**:
   ```bash
   # For user installation
   export PATH="$PATH:$HOME/.local/bin"
   echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
   
   # Reload shell configuration
   source ~/.bashrc
   ```

5. **Reinstall properly**:
   ```bash
   # User installation (recommended)
   pip3 install --user --force-reinstall /path/to/swahili-subtitle-translator
   
   # System installation (requires sudo)
   sudo pip3 install --force-reinstall /path/to/swahili-subtitle-translator
   ```

6. **Use the automated installation script**:
   ```bash
   cd swahili-subtitle-translator
   chmod +x install_global.sh
   ./install_global.sh
   ```

7. **Test from different directory**:
   ```bash
   cd ~/Desktop
   sst --help  # Should work from anywhere
   ```

**For Windows Git Bash Users**:
```bash
# Check if Python Scripts directory is in PATH
echo $PATH | grep -i python

# Add Python Scripts to PATH (typical location)
export PATH="$PATH:/c/Users/$USER/AppData/Local/Programs/Python/Python*/Scripts"

# Or use the installation script which handles this automatically
./install_global.sh
```

### Import Errors

**Problem**: `ModuleNotFoundError` or import errors

**Solutions**:
1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Use virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip3 install -r requirements.txt
   ```

### Translation Service Errors

**Problem**: Translation fails or "Service unavailable"

**Solutions**:
1. **Check internet connection**
2. **Try different service**:
   ```bash
   python3 -m swahili_subtitle_translator.cli.main movie.srt --service google
   ```
3. **Increase retry attempts**:
   ```bash
   python3 -m swahili_subtitle_translator.cli.main movie.srt --max-retries 5
   ```

### Permission Errors

**Problem**: Permission denied errors

**Solutions**:
1. **Check file permissions**:
   ```bash
   chmod 644 your_subtitle_file.srt
   ```
2. **Use different output directory**:
   ```bash
   python3 -m swahili_subtitle_translator.cli.main movie.srt -o ~/translated_movie.srt
   ```

## 🐛 Known Limitations

- **Translation Quality**: Depends on chosen translation service
- **Complex Formatting**: Some advanced subtitle formatting may be lost
- **Rate Limits**: Translation services have usage limits
- **Context Awareness**: May not understand complex narrative context

## 📚 Examples

Check out the [examples/](examples/) directory for:

- Sample subtitle files
- Batch processing scripts  
- Integration examples
- Configuration templates

## ❓ FAQ

**Q: Is this tool free to use?**
A: Yes, the tool is open-source and free. However, translation services may have usage limits.

**Q: Can I use other translation services?**
A: Currently supports Google Translate and MyMemory. More services can be added.

**Q: How accurate are the translations?**
A: Typically 85-90% accuracy. Manual review recommended for professional use.

**Q: Can I translate to languages other than Swahili?**
A: Currently optimized for English to Swahili. Other languages can be added.

**Q: Does it work offline?**
A: No, internet connection required for translation services.

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/andersonchale/swahili-subtitle-translator/issues)
- **Documentation**: Check the [docs/](docs/) directory
- **Discussions**: Use GitHub Discussions for questions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Translation Services**: Google Translate and MyMemory for API access
- **Subtitle Libraries**: pysrt and other subtitle parsing libraries
- **Community**: Contributors and users who help improve the tool
- **Swahili Language**: Rich cultural heritage that inspired this project

## 🚀 Future Plans

- [ ] GUI Application with drag-and-drop interface
- [ ] Additional translation service integrations
- [ ] Real-time subtitle translation for live content
- [ ] Mobile app for on-the-go translation
- [ ] Plugin support for video editing software
- [ ] Advanced AI-powered cultural adaptation
- [ ] Support for more African languages

---

**Made with ❤️ by Anderson**

*Star ⭐ this repository if you find it helpful!*
