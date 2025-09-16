#!/bin/bash
# Global Installation Script for Swahili Subtitle Translator
# This script makes the CLI commands globally available on Linux, macOS, and Windows (Git Bash)

set -e

echo "🚀 Installing Swahili Subtitle Translator globally..."

# Detect the operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "Detected: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "Detected: macOS"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
    echo "Detected: Windows (Git Bash)"
else
    OS="unknown"
    echo "Detected: Unknown OS ($OSTYPE)"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python 3 is available
if ! command_exists python3; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found: $PYTHON_VERSION"

# Check if pip is available
if ! command_exists pip3; then
    echo "❌ Error: pip3 is not installed or not in PATH"
    exit 1
fi

echo "✓ Found: pip3"

# Install method selection
echo ""
echo "Choose installation method:"
echo "1. System-wide installation (requires sudo/admin rights, may fail on modern systems)"
echo "2. User installation (--user flag, no admin rights needed, recommended)"
echo "3. Virtual environment (recommended for development)"
echo "4. Pipx installation (recommended for modern Python, installs if missing)"
echo ""
read -p "Enter your choice (1-4): " CHOICE

case $CHOICE in
    1)
        echo "🔧 Installing system-wide..."
        if [[ "$OS" == "windows" ]]; then
            # Windows doesn't have sudo
            pip3 install .
        else
            # Try system installation, handle PEP 668 externally-managed environments
            if sudo pip3 install . 2>/dev/null; then
                echo "✅ System-wide installation successful"
            else
                echo "⚠️  System installation failed (externally-managed environment)"
                echo "📝 This is common on modern Ubuntu/Debian systems (PEP 668)"
                echo ""
                echo "🔄 Trying alternative methods:"
                
                # Try with pipx if available
                if command_exists pipx; then
                    echo "📦 Installing with pipx..."
                    pipx install .
                    echo "✅ Installed with pipx - commands should be globally available"
                elif command_exists apt; then
                    echo "📋 Option 1: Install pipx (recommended for global app installation)"
                    echo "   sudo apt update && sudo apt install -y pipx"
                    echo "   pipx install ."
                    echo ""
                    echo "📋 Option 2: Use --break-system-packages (not recommended)"
                    echo "   sudo pip3 install --break-system-packages ."
                    echo ""
                    echo "📋 Option 3: Switch to user installation (recommended)"
                    echo ""
                    read -p "Would you like to try user installation instead? (y/n): " SWITCH_TO_USER
                    if [[ "$SWITCH_TO_USER" =~ ^[Yy]$ ]]; then
                        echo "🔄 Switching to user installation..."
                        echo ""
                        echo "🔧 Installing for current user..."
                        pip3 install --user .
                        
                        # Add user bin to PATH if not already there
                        USER_BIN_PATH="$HOME/.local/bin"
                        
                        if [[ ":$PATH:" != *":$USER_BIN_PATH:"* ]]; then
                            echo "📝 Adding $USER_BIN_PATH to PATH..."
                            
                            # Determine which shell config file to use
                            if [[ -f "$HOME/.bashrc" ]]; then
                                SHELL_CONFIG="$HOME/.bashrc"
                            elif [[ -f "$HOME/.bash_profile" ]]; then
                                SHELL_CONFIG="$HOME/.bash_profile"
                            elif [[ -f "$HOME/.zshrc" ]]; then
                                SHELL_CONFIG="$HOME/.zshrc"
                            else
                                SHELL_CONFIG="$HOME/.profile"
                            fi
                            
                            echo "export PATH=\"\$PATH:$USER_BIN_PATH\"" >> "$SHELL_CONFIG"
                            echo "✅ Added PATH export to $SHELL_CONFIG"
                            echo "⚠️  Please restart your terminal or run: source $SHELL_CONFIG"
                            
                            # Also export for current session
                            export PATH="$PATH:$USER_BIN_PATH"
                        fi
                    else
                        echo "❌ System installation aborted"
                        exit 1
                    fi
                else
                    echo "❌ System installation failed and no alternative package manager found"
                    echo "💡 Please choose user installation (option 2) instead"
                    exit 1
                fi
            fi
        fi
        ;;
    2)
        # Only run this if we didn't already do user installation from option 1 fallback
        if [[ "$SWITCH_TO_USER" != "y" && "$SWITCH_TO_USER" != "Y" ]]; then
            echo "🔧 Installing for current user..."
            pip3 install --user .
            
            # Add user bin to PATH if not already there
            USER_BIN_PATH="$HOME/.local/bin"
            
            if [[ ":$PATH:" != *":$USER_BIN_PATH:"* ]]; then
                echo "📝 Adding $USER_BIN_PATH to PATH..."
                
                # Determine which shell config file to use
                if [[ -f "$HOME/.bashrc" ]]; then
                    SHELL_CONFIG="$HOME/.bashrc"
                elif [[ -f "$HOME/.bash_profile" ]]; then
                    SHELL_CONFIG="$HOME/.bash_profile"
                elif [[ -f "$HOME/.zshrc" ]]; then
                    SHELL_CONFIG="$HOME/.zshrc"
                else
                    SHELL_CONFIG="$HOME/.profile"
                fi
                
                echo "export PATH=\"\$PATH:$USER_BIN_PATH\"" >> "$SHELL_CONFIG"
                echo "✅ Added PATH export to $SHELL_CONFIG"
                echo "⚠️  Please restart your terminal or run: source $SHELL_CONFIG"
                
                # Also export for current session
                export PATH="$PATH:$USER_BIN_PATH"
            fi
        fi
        ;;
    3)
        echo "🔧 Setting up virtual environment..."
        
        # Create virtual environment if it doesn't exist
        if [[ ! -d ".venv" ]]; then
            python3 -m venv .venv
            echo "✓ Created virtual environment"
        fi
        
        # Activate virtual environment
        source .venv/bin/activate
        echo "✓ Activated virtual environment"
        
        # Install in editable mode
        pip install -e .
        echo "✓ Installed in development mode"
        
        echo ""
        echo "🎯 To use the CLI commands, activate the virtual environment:"
        echo "   source $(pwd)/.venv/bin/activate"
        echo "   sst --help"
        echo ""
        ;;
    4)
        echo "🔧 Installing with pipx..."
        
        # Check if pipx is available
        if ! command_exists pipx; then
            echo "📦 pipx not found. Installing pipx first..."
            if command_exists apt; then
                sudo apt update && sudo apt install -y pipx
            elif command_exists brew; then
                brew install pipx
            elif command_exists dnf; then
                sudo dnf install -y pipx
            elif command_exists yum; then
                sudo yum install -y pipx
            else
                echo "⚠️  Could not install pipx automatically. Please install it manually:"
                echo "   Ubuntu/Debian: sudo apt install pipx"
                echo "   macOS: brew install pipx"
                echo "   Fedora: sudo dnf install pipx"
                echo "   Other: pip install --user pipx"
                exit 1
            fi
            
            # Ensure pipx is in PATH
            pipx ensurepath 2>/dev/null || true
            echo "✅ pipx installed successfully"
        fi
        
        # Install with pipx
        pipx install .
        echo "✅ Installed with pipx - commands should be globally available"
        ;;
    *)
        echo "❌ Invalid choice. Please enter 1, 2, 3, or 4."
        exit 1
        ;;
esac

# Test the installation
echo ""
echo "🧪 Testing installation..."

# Refresh command cache
hash -r 2>/dev/null || true

# Test both commands
if command_exists sst; then
    echo "✓ sst command is available"
    sst --help >/dev/null && echo "✓ sst --help works"
else
    echo "❌ sst command not found"
fi

if command_exists swahili-sub-translate; then
    echo "✓ swahili-sub-translate command is available"
    swahili-sub-translate --help >/dev/null && echo "✓ swahili-sub-translate --help works"
else
    echo "❌ swahili-sub-translate command not found"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📚 Usage examples:"
echo "   sst search \"The Matrix\" --limit 5"
echo "   sst pipeline \"Inception\" --output inception_swahili.srt"
echo "   swahili-sub-translate translate movie.srt"
echo ""
echo "🔍 For more help:"
echo "   sst --help"
echo "   sst search --help"
echo "   sst pipeline --help"
echo ""

# Check if commands work globally by testing from different directory
TEST_DIR="/tmp/sst_test_$$"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

if sst --help >/dev/null 2>&1; then
    echo "✅ Global installation successful - commands work from any directory!"
else
    echo "⚠️  Commands may not be globally available. Try:"
    echo "   - Restart your terminal"
    echo "   - Run: hash -r"
    echo "   - Check your PATH: echo \$PATH"
fi

# Cleanup
cd - >/dev/null
rm -rf "$TEST_DIR"
