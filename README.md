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

### Method 1: Direct Usage (Recommended for beginners)

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/swahili-subtitle-translator.git
cd swahili-subtitle-translator
```

2. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

3. **Use directly with Python:**
```bash
# Translate a single subtitle file
python3 -m swahili_subtitle_translator.cli.main movie.srt

# Show help
python3 -m swahili_subtitle_translator.cli.main --help

# Translate with statistics
python3 -m swahili_subtitle_translator.cli.main movie.srt --stats
```

### Method 2: Install as Package (Advanced users)

1. **Clone and install in development mode:**
```bash
git clone https://github.com/yourusername/swahili-subtitle-translator.git
cd swahili-subtitle-translator
pip3 install -e .
```

2. **Use the installed command:**
```bash
# Now you can use the command directly
swahili-sub-translate movie.srt
sst movie.srt  # Short alias
```

### Method 3: Install from PyPI (Future - when published)

```bash
# Install from PyPI (when published)
pip3 install swahili-subtitle-translator

# Use directly
swahili-sub-translate movie.srt
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
git clone https://github.com/yourusername/swahili-subtitle-translator.git
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

**Problem**: `swahili-sub-translate: command not found`

**Solutions**:
1. **Use Method 1 (Direct Python)** - No installation needed:
   ```bash
   python3 -m swahili_subtitle_translator.cli.main movie.srt
   ```

2. **Install the package properly**:
   ```bash
   cd swahili-subtitle-translator
   pip3 install -e .
   # Then use: swahili-sub-translate movie.srt
   ```

3. **Check your PATH**:
   ```bash
   echo $PATH
   # Make sure ~/.local/bin is in your PATH
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

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/swahili-subtitle-translator/issues)
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
