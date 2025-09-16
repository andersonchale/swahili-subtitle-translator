# CLI Global Availability - Setup Guide

## ✅ Current Status

The CLI commands `sst` and `swahili-sub-translate` are now **GLOBALLY AVAILABLE** and working from any directory!

## 🌟 Quick Test

```bash
# Test from any directory
cd ~/Desktop
sst --help

cd /tmp
swahili-sub-translate --help

# These should work from anywhere!
sst search "The Matrix" --limit 3
sst pipeline "Inception" --output inception_swahili.srt
```

## 🚀 Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
cd swahili-subtitle-translator
chmod +x install_global.sh
./install_global.sh
```

This script:
- ✅ Detects your OS (Linux/macOS/Windows Git Bash)
- ✅ Offers multiple installation options
- ✅ Handles PATH configuration automatically
- ✅ Tests the installation

### Method 2: Manual User Installation

```bash
# Install for current user (no sudo needed)
pip3 install --user /path/to/swahili-subtitle-translator

# Add to PATH if needed
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc

# Refresh command cache
hash -r
```

### Method 3: System-Wide Installation

```bash
# Install system-wide (requires sudo on Linux/macOS)
sudo pip3 install /path/to/swahili-subtitle-translator

# Refresh command cache
hash -r
```

## 🔧 Troubleshooting

### "Command not found" Error

**Most common fix:**
```bash
hash -r
sst --help  # Try again
```

**Check if installed:**
```bash
which sst
ls -la ~/.local/bin/ | grep sst
```

**Check PATH:**
```bash
echo $PATH
# Should include ~/.local/bin or /usr/local/bin
```

**Force reinstall:**
```bash
pip3 install --user --force-reinstall /path/to/swahili-subtitle-translator
hash -r
```

### Platform-Specific Solutions

**Linux/Ubuntu:**
```bash
# Add to PATH
export PATH="$PATH:$HOME/.local/bin"
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

**macOS:**
```bash
# Add to PATH
export PATH="$PATH:$HOME/.local/bin"
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc
source ~/.zshrc
```

**Windows Git Bash:**
```bash
# Check Python Scripts in PATH
echo $PATH | grep -i python

# Add if missing
export PATH="$PATH:/c/Users/$USER/AppData/Local/Programs/Python/Python*/Scripts"
```

## 📱 Usage Examples

Once globally installed, you can use these commands from anywhere:

### Basic Usage
```bash
# Search for subtitles
sst search "The Dark Knight" --limit 5

# Complete pipeline (search + download + translate)
sst pipeline "Inception" --output inception_swahili.srt

# Translate existing subtitle file
swahili-sub-translate translate movie.srt --service google_translate
```

### Advanced Usage
```bash
# TV show pipeline
sst pipeline "Breaking Bad" --season 1 --episode 1 --year 2008 \
    --output breaking_bad_s01e01_swahili.srt

# Search specific sources
sst search "Avatar" --sources opensubtitles subscene --limit 10

# Custom translation service
sst pipeline "The Matrix" --service mock --target-language sw
```

## 🎯 Verification Tests

Run these to ensure global availability:

```bash
# Test 1: Command existence
command -v sst && echo "✅ sst found" || echo "❌ sst not found"
command -v swahili-sub-translate && echo "✅ swahili-sub-translate found" || echo "❌ not found"

# Test 2: Help command from different directories
cd ~/Desktop && sst --help >/dev/null && echo "✅ Works from Desktop"
cd /tmp && sst --help >/dev/null && echo "✅ Works from /tmp"
cd ~ && sst --help >/dev/null && echo "✅ Works from home"

# Test 3: Subcommand help
sst search --help >/dev/null && echo "✅ Search command works"
sst pipeline --help >/dev/null && echo "✅ Pipeline command works"
```

## 🛠️ Development Setup

For contributors and developers:

```bash
# Clone and setup development environment
git clone https://github.com/andersonchale/swahili-subtitle-translator.git
cd swahili-subtitle-translator

# Option 1: Virtual environment (isolated)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Option 2: User installation (global)
pip3 install --user -e .

# Test installation
sst --help
```

## 📝 Notes

- **Virtual Environment**: Commands only work when venv is activated
- **User Installation**: Commands work globally but only for current user
- **System Installation**: Commands work globally for all users
- **PATH Issues**: Most problems are solved with `hash -r` or PATH configuration
- **Windows**: Use Git Bash for best compatibility

## 🔍 Support

If you encounter issues:

1. Try `hash -r` first
2. Check PATH with `echo $PATH`
3. Verify installation with `which sst`
4. Use the automated installation script
5. Restart terminal/shell

The CLI is designed to work seamlessly across Linux, macOS, and Windows (Git Bash) environments.
