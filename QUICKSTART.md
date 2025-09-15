# 🚀 Quick Start Guide

## For Beginners (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/swahili-subtitle-translator.git
cd swahili-subtitle-translator
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Use the Tool Directly
```bash
# Translate a subtitle file
python3 -m swahili_subtitle_translator.cli.main your_movie.srt

# Show help
python3 -m swahili_subtitle_translator.cli.main --help

# Translate with statistics
python3 -m swahili_subtitle_translator.cli.main your_movie.srt --stats
```

That's it! No complex installation needed.

## For Advanced Users

### Install as Package
```bash
git clone https://github.com/yourusername/swahili-subtitle-translator.git
cd swahili-subtitle-translator
pip3 install -e .
```

### Use Short Commands
```bash
swahili-sub-translate your_movie.srt
# OR
sst your_movie.srt
```

## Test with Sample File
```bash
# Create a test file
cat > test.srt << 'EOF'
1
00:00:01,000 --> 00:00:04,000
Hello world, this is a test.

2
00:00:05,000 --> 00:00:08,000
Winter is coming.
EOF

# Translate it (Method 1)
python3 -m swahili_subtitle_translator.cli.main test.srt --stats

# Check the result
cat test_swahili.srt
```

## Common Issues

**Problem**: `command not found`
**Solution**: Use Method 1 (Direct Python usage)

**Problem**: Import errors
**Solution**: Run `pip3 install -r requirements.txt`

**Problem**: Translation fails
**Solution**: Check internet connection and try again

---
**Made with ❤️ by Anderson**
