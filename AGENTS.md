# AGENTS.md

## Project Overview

YouTube Video Transcriber - A Python CLI tool that downloads YouTube videos and transcribes them to text using OpenAI's Whisper model. Supports CUDA acceleration and multiple languages.

**Tech Stack:** Python 3.13+, PyTorch (CUDA 12.8), Whisper, yt-dlp, Pydantic, UV (package manager)
**Main Entry Point:** `yt_transcriber/cli.py`
**Architecture:** Modular CLI with separate components for downloading, transcription, config, and utilities

## Project Structure

```
yt-video-summarizer/
├── yt_transcriber/          # Main package
│   ├── cli.py              # CLI entry point and orchestration
│   ├── config.py           # Pydantic settings (reads .env)
│   ├── downloader.py       # YouTube video downloading (yt-dlp)
│   ├── transcriber.py      # Whisper transcription logic
│   └── utils.py            # Shared utilities
├── test/                    # Test suite
│   ├── conftest.py         # Pytest fixtures
│   ├── test_infrastructure.py  # Infrastructure tests
│   └── check_pytorch_cuda.py  # CUDA availability validator
├── temp_files/             # Temporary media storage (auto-cleaned)
├── output_transcripts/     # Final transcript outputs
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
# Using Make (shows help if no URL provided)
make run

# With URL
make run URL="https://www.youtube.com/watch?v=VIDEO_ID"

# Direct UV command (more options)
uv run python -m yt_transcriber.cli --url "https://www.youtube.com/watch?v=VIDEO_ID"

# With custom FFmpeg location (Windows)
uv run python -m yt_transcriber.cli --url "URL" --ffmpeg-location "C:\ffmpeg\bin\ffmpeg.exe"

# With specific language
uv run python -m yt_transcriber.cli --url "URL" --language es

# Show all available options
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

# Logging
LOG_LEVEL=INFO                   # Options: DEBUG, INFO, WARNING, ERROR

# Directories (auto-created if missing)
TEMP_DIR=temp_files
OUTPUT_DIR=output_transcripts
```

### Security Best Practices

- **Never commit** `.env` files or credentials
- Update `.env.example` when adding new configuration options
- Use **Pydantic Settings** for configuration management
- Avoid hardcoding paths or secrets in code
- Expose all configurable values through environment variables

## Dependencies & Compatibility

### Core Dependencies

- **PyTorch** (CUDA 12.8 compatible)
- **Whisper** (OpenAI)
- **yt-dlp** (YouTube downloader)
- **Pydantic** (configuration management)

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
