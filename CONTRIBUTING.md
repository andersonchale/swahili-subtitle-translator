# Contributing to Swahili Subtitle Translator

Thank you for your interest in contributing to the Swahili Subtitle Translator! 🎉

This document provides guidelines and instructions for contributing to this project. By participating in this project, you agree to abide by our code of conduct.

## 🤝 Ways to Contribute

### 1. Reporting Bugs
- Use the GitHub Issues template for bug reports
- Provide detailed information about the bug
- Include steps to reproduce the issue
- Mention your operating system and Python version

### 2. Suggesting Enhancements
- Use GitHub Issues to suggest new features
- Clearly describe the enhancement and its benefits
- Consider if it aligns with the project's goals

### 3. Code Contributions
- Fix bugs or implement new features
- Improve documentation
- Add or improve tests
- Optimize performance

### 4. Documentation
- Improve README documentation
- Add code comments and docstrings
- Create tutorials or examples
- Translate documentation

## 🚀 Getting Started

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/swahili-subtitle-translator.git
   cd swahili-subtitle-translator
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Make your changes** in your feature branch
2. **Write tests** for new functionality
3. **Run the test suite**:
   ```bash
   pytest
   ```
4. **Format your code**:
   ```bash
   black .
   ```
5. **Lint your code**:
   ```bash
   flake8 swahili_subtitle_translator
   ```
6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request** on GitHub

## 📝 Coding Standards

### Python Style Guide
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Maximum line length: 88 characters (Black default)
- Use type hints where appropriate

### Code Formatting
- Use **Black** for code formatting
- Use **flake8** for linting
- Use **mypy** for type checking (optional but recommended)

### Documentation
- Write clear docstrings for all functions and classes
- Use Google-style docstrings
- Include examples in docstrings when helpful
- Update README.md for significant changes

### Example Docstring Format:
```python
def translate_text(self, text: str, progress_callback=None) -> str:
    """
    Translate a single text string.
    
    Args:
        text: Text to translate
        progress_callback: Optional callback for progress updates
        
    Returns:
        Translated text
        
    Raises:
        TranslationError: If translation fails
        
    Example:
        >>> translator = SubtitleTranslator()
        >>> result = translator.translate_text("Hello world")
        >>> print(result)
        'Hujambo dunia'
    """
```

## 🧪 Testing Guidelines

### Writing Tests
- Write tests for all new features
- Include both unit tests and integration tests
- Test edge cases and error conditions
- Aim for high test coverage (>80%)

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=swahili_subtitle_translator

# Run specific test file
pytest tests/test_translator.py

# Run with verbose output
pytest -v
```

### Test Structure
```
tests/
├── __init__.py
├── test_translator.py        # Core translation tests
├── test_processor.py         # Subtitle processing tests
├── test_cli.py              # CLI interface tests
├── test_utils.py            # Utility function tests
└── fixtures/                # Test data files
    ├── sample.srt
    ├── sample.ass
    └── sample.vtt
```

## 📚 Project Architecture

### Key Components
- **Core Module**: Translation engine and subtitle processing
- **CLI Module**: Command-line interface and user interaction
- **Utils Module**: Helper functions, caching, and format handling

### Adding New Features
1. **Translation Services**: Add new services in `core/translator.py`
2. **Subtitle Formats**: Add format support in `utils/formats.py` and `core/processor.py`
3. **CLI Commands**: Extend the CLI in `cli/main.py`
4. **Utilities**: Add helper functions in appropriate utils modules

## 🐛 Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Behavior**: What should have happened
- **Actual Behavior**: What actually happened
- **Environment**: 
  - Operating System
  - Python version
  - Package version
- **Files**: Sample subtitle files if applicable
- **Logs**: Error messages or log output

## 💡 Feature Requests

For feature requests, please provide:

- **Use Case**: Why is this feature needed?
- **Description**: Detailed description of the feature
- **Alternatives**: Any alternative solutions considered
- **Implementation Ideas**: If you have ideas on how to implement it

## 🔍 Code Review Process

### What We Look For
- **Functionality**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Style**: Does it follow our coding standards?
- **Performance**: Are there any performance considerations?

### Review Timeline
- We aim to review pull requests within 2-3 days
- Complex changes may take longer
- We may request changes before merging

## 📋 Pull Request Template

When creating a pull request:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code cleanup

## Testing
- [ ] Tests pass locally
- [ ] New tests added for changes
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or marked as such)
```

## 🌍 Translation Contributions

### Improving Swahili Translations
- Help improve cultural adaptations
- Add common phrase translations
- Fix grammatical issues in output
- Add region-specific terminology

### Adding Language Support
- Extend the tool to support other languages
- Add new translation service integrations
- Implement language-specific post-processing

## 📱 Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Focus on constructive feedback
- Be patient with newcomers

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code contributions and reviews

## 🎯 Good First Issues

Looking for a place to start? Check out issues labeled:
- `good first issue`: Perfect for newcomers
- `help wanted`: We need community assistance
- `documentation`: Improve docs
- `enhancement`: New features to implement

## 🚦 Development Status

### Current Focus Areas
- Improving translation quality
- Adding more subtitle formats
- Performance optimizations
- Better error handling
- GUI development

### Future Goals
- Mobile app development
- Real-time translation
- Plugin ecosystem
- Multi-language support

## 📞 Getting Help

If you need help with contributing:

1. **Check existing issues** and documentation first
2. **Create a GitHub Discussion** for general questions
3. **Open an issue** for specific problems
4. **Join our community** discussions

## 🙏 Recognition

All contributors will be:
- Listed in the project's contributors
- Acknowledged in release notes
- Given credit for their contributions

Thank you for helping make subtitle translation more accessible! 🌟

---

**Note**: This contributing guide is a living document. Please suggest improvements by opening an issue or pull request.
