# AGENTS.md

## Project Overview

YouTube Video Transcriber & Script Generator - A Python CLI tool with dual functionality:

1. **Video Transcriber**: Downloads YouTube videos and transcribes them to text using OpenAI's Whisper model with CUDA acceleration
2. **Script Generator**: Analyzes successful YouTube videos in your niche and generates AI-powered scripts using Google's Gemini API

**Tech Stack:** Python 3.13+, PyTorch (CUDA 12.8), Whisper, yt-dlp, Pydantic, Google Gemini API, UV (package manager)
**Main Entry Points:**

- `yt_transcriber/cli.py` - Main CLI with subcommands (transcribe, generate-script)
- `youtube_script_generator/` - Script generation pipeline (6 phases)

**Architecture:** Modular CLI with two independent workflows:

- **Transcription Pipeline**: Download → Transcribe → Save
- **Script Generation Pipeline**: Query Optimization → YouTube Search → Batch Download/Transcribe → Pattern Analysis → Synthesis → Script Generation

## Project Structure

```
yt-video-summarizer/
├── yt_transcriber/          # Main package (transcription)
│   ├── cli.py              # CLI entry point with subcommands
│   ├── config.py           # Pydantic settings (reads .env)
│   ├── downloader.py       # YouTube video downloading (yt-dlp)
│   ├── transcriber.py      # Whisper transcription logic
│   └── utils.py            # Shared utilities
├── youtube_script_generator/  # Script generation pipeline (NEW)
│   ├── models.py           # Dataclasses (YouTubeVideo, VideoAnalysis, etc.)
│   ├── query_optimizer.py  # AI query optimization with Gemini
│   ├── youtube_searcher.py # YouTube search with quality filtering
│   ├── batch_processor.py  # Parallel video processing
│   ├── pattern_analyzer.py # Pattern extraction from transcripts
│   ├── synthesizer.py      # Pattern aggregation and synthesis
│   └── script_generator.py # Script generation with SEO
├── test/                    # Test suite
│   ├── conftest.py         # Pytest fixtures
│   ├── test_infrastructure.py        # Infrastructure tests (4 tests)
│   ├── test_youtube_script_generator.py  # Script generator tests (18 tests)
│   └── check_pytorch_cuda.py  # CUDA availability validator
├── docs/                    # Documentation (NEW)
│   └── YOUTUBE_SCRIPT_GENERATOR.md  # Comprehensive script generator guide
├── temp_files/             # Temporary media storage (auto-cleaned)
├── temp_batch/             # Temporary batch processing files (NEW)
├── output_transcripts/     # Transcript outputs
├── output_scripts/         # Generated scripts with SEO (NEW)
├── output_analysis/        # Pattern synthesis reports (NEW)
├── Makefile                # Development commands (setup, test, lint, etc.)
├── pyproject.toml          # Project metadata and dependencies (UV/pip)
├── .env                    # Environment config (not committed)
└── .env.example           # Template for required env vars
```

## Setup Commands

### 🚀 Quick Start (Recommended)

The fastest way to set up the development environment using **Makefile** (cross-platform):

```bash
# Works on Linux/macOS/Windows (requires Make installed)
make setup

# This will:
# 1. Verify UV is installed (or show installation instructions)
# 2. Create Python 3.13 virtual environment
# 3. Install all dependencies (including dev tools)
# 4. Install PyTorch with CUDA 12.8 (Windows/Linux) or MPS (macOS)
# 5. Verify CUDA/MPS availability
# 6. Run test suite to validate installation
```

**Time**: ~3-5 minutes | **What you get**: Fully configured environment ready for development

**Windows users without Make?**

- **Quick install**: `scoop install make` or `choco install make`
- **Detailed guide**: See [.github/SETUP_MAKE.md](.github/SETUP_MAKE.md)

---

### ⚙️ Manual Setup (Alternative)

If you prefer step-by-step control or the script fails:

#### Option A: Modern Setup with UV (Recommended)

```powershell
# 1. Install UV (Python package manager - 10-100x faster than pip)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Create virtual environment
uv venv --python 3.13

# 3. Install dependencies (including dev tools)
uv sync --extra dev

# 4. ⚠️ CRITICAL: Install PyTorch with CUDA (separate step required!)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --force-reinstall

# 5. Verify CUDA is working
uv run python test/check_pytorch_cuda.py
# Expected output: "CUDA available: True"

# 6. Run tests to verify everything works
uv run pytest
```

**⚠️ IMPORTANT NOTE ON PYTORCH CUDA**:

PyTorch with CUDA **cannot** be installed directly via `uv sync` due to UV's dependency resolver limitations with PyTorch's custom CUDA index. You **must** run step 4 manually after `uv sync --extra dev`, or use `make setup` which automates this.

**Why?** PyTorch CUDA wheels are hosted on a custom index (`https://download.pytorch.org/whl/cu128`), not standard PyPI. UV attempts to resolve all dependencies from this index, causing conflicts with packages like `markupsafe` that only have Linux builds there.

**Solution**: Install base dependencies from PyPI first (`uv sync --extra dev`), then forcefully replace PyTorch CPU with CUDA version using direct index access.

#### Option B: Legacy Setup with pip/venv

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env
```

**Note**: `requirements.txt` is maintained for backward compatibility but UV (`pyproject.toml`) is preferred for new setups.

---

### Verify CUDA Setup (GPU acceleration)

### Verify CUDA Setup (GPU acceleration)

```bash
# Check if CUDA is available
uv run python test/check_pytorch_cuda.py

# Expected output if CUDA is working:
# PyTorch version: 2.8.0+cu128
# CUDA available: True
# CUDA version: 12.8
# GPU name: NVIDIA GeForce RTX XXXX
```

**If you see "CUDA available: False"**, PyTorch CPU was installed instead of CUDA. See [Troubleshooting](#troubleshooting) below.

---

## Development Commands

## Development Commands

### Common Tasks (Using Makefile)

```bash
# Show all available commands
make help

# Complete setup (works on all platforms)
make setup

# Run all quality checks (lint + format + typecheck + test)
make check

# Run tests
make test                    # Run all tests
make test-v                  # Run tests with verbose output
make test-cov                # Run tests with coverage report
make test-cuda               # Verify CUDA availability

# Code quality
make lint                    # Run linter (Ruff check)
make lint-fix                # Run linter and auto-fix issues
make format                  # Format code with Ruff
make format-check            # Check formatting without modifying
make typecheck               # Run type checker (Mypy)

# Cleanup
make clean                   # Remove temporary files and caches
make clean-all               # Remove temp files AND virtual environment

# Utilities
make update                  # Update dependencies to latest versions
make show-env                # Show Python environment information
```

### Pre-commit Hooks

Pre-commit hooks run automatically before every commit to ensure code quality:

```bash
# Hooks are installed automatically by 'make setup'
# To manually install hooks:
uv run pre-commit install

# Run hooks manually on all files
uv run pre-commit run --all-files

# Run hooks on staged files only
uv run pre-commit run
```

**What the hooks check:**

- ✅ Ruff linting (with auto-fix)
- ✅ Ruff formatting
- ✅ Large files (>1MB)
- ✅ Merge conflicts
- ✅ YAML/TOML syntax
- ✅ Trailing whitespace
- ✅ End of file newlines
- ✅ Debug statements

**Note**: Type checking (Mypy) is run via `make typecheck`, not in pre-commit hooks, to keep commits fast.

### Run the CLI

```bash
# Transcribe a video
make run URL="https://www.youtube.com/watch?v=VIDEO_ID"

# Or use direct UV command with subcommand
uv run python -m yt_transcriber.cli transcribe --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Generate a script from your niche
uv run python -m yt_transcriber.cli generate-script --idea "Your video topic"

# With more options
uv run python -m yt_transcriber.cli generate-script \
  --idea "Python async tutorial" \
  --max-videos 10 \
  --duration 15 \
  --style "casual and educational"

# Show all available options for each command
uv run python -m yt_transcriber.cli transcribe --help
uv run python -m yt_transcriber.cli generate-script --help
uv run python -m yt_transcriber.cli --help
```

### Testing (Direct UV Commands)

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=yt_transcriber --cov-report=html

# Run specific test file
uv run pytest test/test_infrastructure.py -v

# Run CUDA check
uv run python test/check_pytorch_cuda.py
```

### Code Quality (Direct UV Commands)

```bash
# Run linter (Ruff)
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type checking (Mypy)
uv run mypy --package yt_transcriber

# Run all quality checks
uv run ruff check . && uv run ruff format --check . && uv run mypy --package yt_transcriber && uv run pytest
```

---

## Troubleshooting

### Problem: "CUDA available: False" after setup

**Cause**: PyTorch was installed in CPU-only mode instead of CUDA.

**Solution**:

```powershell
# Reinstall PyTorch with CUDA support
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --force-reinstall

# Verify CUDA is now working
uv run python test/check_pytorch_cuda.py
```

### Problem: "No solution found when resolving dependencies"

**Cause**: UV cache is corrupted or `uv.lock` has stale data.

**Solution**:

```powershell
# Clean UV cache
uv cache clean

# Remove lock file
Remove-Item uv.lock -ErrorAction SilentlyContinue

# Reinstall dependencies
uv sync
```

### Problem: `uv sync` installs wrong package versions

**Cause**: Lock file is out of sync with `pyproject.toml`.

**Solution**:

```powershell
# Remove lock file and reinstall
Remove-Item uv.lock
uv sync
```

### Problem: Tests fail after fresh installation

**Cause**: Dependencies not properly installed or CUDA issues.

**Solution**:

```powershell
# Complete clean reinstall
Remove-Item -Recurse -Force .venv
make setup
```

### Problem: Import errors when running code

**Cause**: Virtual environment not activated or packages not installed.

**Solution**:

```powershell
# Always use 'uv run' to ensure correct environment
uv run python -m yt_transcriber.cli --help

# Or activate venv manually
.\.venv\Scripts\Activate.ps1
python -m yt_transcriber.cli --help
```

---

## Code Style Guidelines

**Python Version:** 3.9+
**Style Guide:** PEP 8

### Naming Conventions

- **Functions/variables:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private members:** `_leading_underscore`

### Best Practices

- Use **explicit type hints** for function signatures
- Write **succinct docstrings** for all public functions and classes
- Use **module logger** instead of print: `logger = logging.getLogger(__name__)`
- Raise **custom exceptions** (`DownloadError`, `TranscriptionError`) for operational errors
- **4-space indentation** (no tabs)
- Keep functions focused and single-purpose

### Example

```python
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def transcribe_video(video_path: Path, language: Optional[str] = None) -> str:
    """Transcribe video file to text using Whisper.

    Args:
        video_path: Path to the video file
        language: Optional ISO language code (e.g., 'en', 'es')

    Returns:
        Transcribed text

    Raises:
        TranscriptionError: If transcription fails
    """
    logger.info(f"Transcribing {video_path}")
    # Implementation...
```

## Testing Guidelines

### Test Organization

- Place test files in `test/` directory
- Name test files `test_*.py` for pytest/unittest compatibility
- Mock network calls and filesystem operations for deterministic tests
- Test both CPU and CUDA code paths when applicable

### Running Tests

```bash
# Run all tests
pytest test/ -v

# Run with coverage
pytest test/ --cov=yt_transcriber --cov-report=html

# Run specific test
pytest test/test_downloader.py::test_download_video -v
```

### Adding Tests

- Write unit tests for new features before implementation
- Include integration tests for CLI workflows
- Document test dependencies in `requirements.txt`
- Update README examples when adding new functionality

## Configuration & Environment Variables

### Required Environment Variables

Configure in `.env` file (never commit this file):

```bash
# Whisper Model Configuration
WHISPER_MODEL_NAME=base          # Options: tiny, base, small, medium, large
WHISPER_DEVICE=cuda              # Options: cuda, cpu

# Google Gemini API (for Script Generator)
GOOGLE_API_KEY=your_api_key_here # Get from: https://aistudio.google.com/apikey

# Logging
LOG_LEVEL=INFO                   # Options: DEBUG, INFO, WARNING, ERROR

# Directories (auto-created if missing)
TEMP_DIR=temp_files
OUTPUT_DIR=output_transcripts
TEMP_BATCH_DIR=temp_batch
OUTPUT_SCRIPTS_DIR=output_scripts
OUTPUT_ANALYSIS_DIR=output_analysis
```

### Security Best Practices

- **Never commit** `.env` files or credentials
- Update `.env.example` when adding new configuration options
- Use **Pydantic Settings** for configuration management
- Avoid hardcoding paths or secrets in code
- Expose all configurable values through environment variables

## YouTube Script Generator Architecture

### Pipeline Overview

The Script Generator implements a 6-phase pipeline for generating AI-powered YouTube scripts:

```
User Idea → [Phase 1] Query Optimization → [Phase 2] YouTube Search →
[Phase 3] Batch Processing → [Phase 4] Pattern Analysis →
[Phase 5] Pattern Synthesis → [Phase 6] Script Generation → Output
```

### Core Components

#### Phase 1: Query Optimizer (`query_optimizer.py`)

- **Purpose**: Transform user ideas into optimized YouTube search queries
- **AI Integration**: Google Gemini API for query enhancement
- **Features**: Stopword removal, trending keyword addition, fallback generation
- **Output**: `OptimizedQuery` with search_query, target_audience, content_type

#### Phase 2: YouTube Searcher (`youtube_searcher.py`)

- **Purpose**: Find high-quality YouTube videos matching the optimized query
- **Integration**: YouTube Data API v3 via `googleapiclient`
- **Filtering**: Duration range (5-45 min), quality ranking (view*count * 0.7 + like*count * 0.3)
- **Output**: List of `YouTubeVideo` with metadata (title, URL, duration, views, quality_score)

#### Phase 3: Batch Processor (`batch_processor.py`)

- **Purpose**: Download and transcribe multiple videos in parallel
- **Integration**: Reuses existing `Downloader` and `Transcriber` from yt_transcriber
- **Features**: Parallel processing, temp file cleanup, quality score calculation
- **Output**: Updated `YouTubeVideo` objects with `transcript_text` and `quality_score`

#### Phase 4: Pattern Analyzer (`pattern_analyzer.py`)

- **Purpose**: Extract 8 pattern categories from video transcripts
- **AI Integration**: Gemini API for structured pattern extraction
- **Patterns Extracted**:
  1. Opening hooks (first 30 seconds)
  2. Pacing metrics (hook duration, content blocks, transitions)
  3. Call-to-actions (CTAs with positions)
  4. Section structure (timestamps and topic flow)
  5. Engagement techniques (questions, storytelling, analogies)
  6. Common vocabulary (technical terms, phrases, title keywords)
  7. Visual/Audio cues (descriptions for editors)
  8. Retention strategies (pattern interrupts, callbacks)
- **Output**: `VideoAnalysis` with effectiveness_score (1-100)

#### Phase 5: Pattern Synthesizer (`synthesizer.py`)

- **Purpose**: Aggregate patterns from multiple analyses into actionable insights
- **Algorithm**: Weighted aggregation using effectiveness_score
- **Features**:
  - Top N extraction (10 hooks, 15 CTAs, 20 vocabulary terms)
  - Frequency analysis with Counter for CTAs and phrases
  - Optimal structure calculation (weighted averages for timing)
  - Gemini-generated synthesis reports (markdown format)
- **Output**: `PatternSynthesis` with aggregated patterns + markdown report

#### Phase 6: Script Generator (`script_generator.py`)

- **Purpose**: Generate complete YouTube scripts from synthesis patterns
- **AI Integration**: Gemini API with pattern-aware prompts
- **Features**:
  - Duration targeting (150 words/min constant)
  - SEO optimization (title, description, tags)
  - Quality scoring (1-100 based on length, structure, SEO)
  - Fallback generation without AI
- **Output**: `GeneratedScript` with markdown content, SEO metadata, quality_score

### Data Models (`models.py`)

All components use strongly-typed dataclasses:

- `YouTubeVideo`: Video metadata + transcript + quality_score
- `OptimizedQuery`: Search parameters + target audience
- `VideoAnalysis`: 8 pattern categories + effectiveness_score
- `PatternSynthesis`: Aggregated patterns + synthesis report
- `GeneratedScript`: Script content + SEO + quality_score

### Integration with Existing Codebase

- **Reuses**: `Downloader`, `Transcriber`, `Settings` from `yt_transcriber`
- **Extends**: CLI with new `generate-script` subcommand
- **Output**: Separate directories (`output_scripts/`, `output_analysis/`)
- **Dependencies**: Adds `google-generativeai`, `google-api-python-client`

### Cost & Performance

- **API Costs**: ~$0.066 per 10 videos (13 Gemini calls)
- **Execution Time**: 8-10 minutes for 10 videos on RTX 3060
  - Download: 1-2 min
  - Transcription: 3-5 min (23 sec/video avg)
  - Pattern Analysis: 2-3 min
  - Synthesis + Generation: <1 min
- **Output Quality**: 85-95 quality score with proper synthesis patterns

For detailed usage examples and troubleshooting, see [docs/YOUTUBE_SCRIPT_GENERATOR.md](docs/YOUTUBE_SCRIPT_GENERATOR.md).

## Dependencies & Compatibility

### Core Dependencies

- **PyTorch** (CUDA 12.8 compatible)
- **Whisper** (OpenAI)
- **yt-dlp** (YouTube downloader)
- **Pydantic** (configuration management)
- **Google Gemini API** (script generation)
- **YouTube Data API v3** (video search)

### System Requirements

- **FFmpeg**: Required for audio processing
  - Windows: Install to `C:\ffmpeg\bin\ffmpeg.exe` or add to PATH
  - Use `--ffmpeg-location` flag if not in PATH

### Adding Dependencies

1. Add to `requirements.txt` with version pinning when critical
2. Verify compatibility with PyTorch/Whisper stack
3. Test on both CPU and CUDA environments
4. Document any system-level requirements in README

## Commit & Pull Request Guidelines

### Commit Message Format

Use conventional commits with module context:

```bash
feat(transcriber): add support for subtitle formats
fix(downloader): handle playlist URLs correctly
refactor(cli): improve error handling for invalid URLs
docs: update CUDA setup instructions
test(transcriber): add unit tests for language detection
```

### PR Checklist

- [ ] Run all tests and ensure they pass
- [ ] Update relevant documentation (README, AGENTS.md)
- [ ] Add/update tests for new functionality
- [ ] Test on both CPU and CUDA (if applicable)
- [ ] Document new environment variables in `.env.example`
- [ ] Include example CLI output for new features
- [ ] Keep commits small and focused
- [ ] Write clear PR description explaining the "why"

### Before Committing

```bash
# Run tests
pytest test/ -v

# Check CUDA compatibility (if modified GPU code)
python test/check_pytorch_cuda.py

# Verify CLI still works
python -m yt_transcriber.cli --help
```

## Common Tasks

### Adding a New Feature

1. Create feature branch: `git checkout -b feat/feature-name`
2. Update relevant module(s) in `yt_transcriber/`
3. Add type hints and docstrings
4. Write unit tests in `test/test_*.py`
5. Update configuration in `config.py` if needed
6. Test manually with sample YouTube URLs
7. Update README with usage examples
8. Commit and create PR

### Debugging Issues

- Check logs in console output (controlled by `LOG_LEVEL`)
- Verify FFmpeg installation: `ffmpeg -version`
- Test CUDA availability: `python test/check_pytorch_cuda.py`
- Check `temp_files/` for downloaded media
- Review `output_transcripts/` for generated files

### Changing Whisper Model

Edit `.env`:

```bash
WHISPER_MODEL_NAME=medium  # or tiny, base, small, large
```

Larger models = better accuracy, slower processing, more VRAM

## Error Handling

### Custom Exceptions

- `DownloadError`: Raised by `downloader.py` for YouTube download failures
- `TranscriptionError`: Raised by `transcriber.py` for Whisper failures

### Usage

```python
from yt_transcriber.downloader import DownloadError

def download_video(url: str) -> Path:
    if not is_valid_url(url):
        raise DownloadError(f"Invalid YouTube URL: {url}")
    # Download logic...
```

## Notes for AI Agents

- Always use **absolute imports**: `from yt_transcriber.config import settings`
- The project uses **Pydantic Settings** for configuration - read from `config.py`, not hardcoded values
- Temporary files are **auto-cleaned** - don't rely on them persisting
- All CLI commands use **module execution**: `python -m yt_transcriber.cli`, not direct file execution
- Windows paths use backslashes: `C:\ffmpeg\bin\ffmpeg.exe`
- When adding features, update both code AND documentation
- Test both **CPU and CUDA paths** when touching transcription logic
