#!/usr/bin/env python3
"""
Setup script for Swahili Subtitle Translator.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    requirements = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('-'):
            requirements.append(line)
    
    return requirements

# Package metadata
setup(
    name="swahili-subtitle-translator",
    version="1.0.0",
    author="Anderson",
    author_email="your.email@example.com",  # Update with your email
    description="Professional subtitle translation tool for English to Swahili",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andersonchale/swahili-subtitle-translator",  # Update with your GitHub URL
    project_urls={
        "Bug Reports": "https://github.com/andersonchale/swahili-subtitle-translator/issues",
        "Source": "https://github.com/andersonchale/swahili-subtitle-translator",
        "Documentation": "https://github.com/andersonchale/swahili-subtitle-translator#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: Swahili",
    ],
    keywords="subtitle, translation, swahili, srt, ass, vtt, cli, automation",
    python_requires=">=3.8",
    install_requires=[
        "pysrt>=1.1.2",
        "deep-translator>=1.11.4", 
        "googletrans==4.0.0rc1",
        "colorama>=0.4.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "full": [
            "ass",  # For ASS/SSA subtitle support
        ]
    },
    entry_points={
        "console_scripts": [
            "swahili-sub-translate=swahili_subtitle_translator.cli:main",
            "sst=swahili_subtitle_translator.cli:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "swahili_subtitle_translator": [
            "py.typed",  # PEP 561 type information
        ],
    },
    zip_safe=False,
    
    # Additional metadata
    license="MIT",
    platforms=["any"],
    
    # Test configuration
    test_suite="tests",
    tests_require=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
)
