#!/usr/bin/env python3
"""
Entry point for running the Swahili Subtitle Translator as a module.

This allows the package to be run with:
    python -m swahili_subtitle_translator
"""

import sys
import os

# Import the main function from CLI
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
