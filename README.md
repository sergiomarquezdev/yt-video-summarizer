# 🎥 YouTube Video Transcriber & Script Generator

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%2012.8-red.svg)](https://pytorch.org/)
[![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen.svg)](test/)
[![Code Coverage](https://img.shields.io/badge/coverage-36%25-yellow.svg)](htmlcov/)

A powerful CLI tool suite for YouTube content creators:

1. **Video Transcriber**: Download and transcribe YouTube videos using OpenAI's Whisper
2. **Script Generator** (NEW): Generate optimized YouTube scripts by learning from successful videos

## ✨ Features

### Web Interface (NEW)

- 🌐 **Gradio web UI** for easy access from any browser
- 📝 **Two-column layout** for transcription and script generation
- 🎨 **Clean, intuitive interface** with real-time progress
- 📥 **One-click downloads** for transcripts and scripts

### Video Transcriber

- 🚀 **Fast transcription** with CUDA GPU acceleration support
- 🌍 **Multi-language support** with automatic language detection
- 📝 **High accuracy** using OpenAI's Whisper models (tiny to large)
- 🔄 **Automatic cleanup** of temporary files

### Script Generator

- 🎬 **AI-powered script generation** from real successful videos
- 🔍 **Pattern analysis** of hooks, structure, CTAs, and vocabulary
- 🧠 **Gemini AI integration** for intelligent synthesis
- ✍️ **SEO optimization** with auto-generated titles, descriptions, and tags
- 📈 **Quality scoring** based on proven patterns
- 🌍 **Automatic bilingual output** (English + Spanish) with technical term preservation

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Web Interface](#-web-interface-new)
- [Usage](#-usage)
  - [Transcribe Videos](#transcribe-videos)
  - [Generate Scripts (NEW)](#generate-scripts-new)
- [Configuration](#️-configuration)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** - [Download here](https://www.python.org/downloads/)
- **FFmpeg** - Required for audio processing
- **CUDA 12.8** (Optional) - For GPU acceleration with NVIDIA GPUs

### FFmpeg Installation

<details>
<summary><b>Windows Installation</b></summary>

1. **Download FFmpeg:**

   - Visit [FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases)
   - Download `ffmpeg-master-latest-win64-gpl-shared.zip`

2. **Install FFmpeg:**

   ```powershell
   # Extract and copy to C:\ffmpeg
   # Verify the installation
   Test-Path "C:\ffmpeg\bin\ffmpeg.exe"
   ```

3. **Choose configuration method:**

   **Option A - Add to PATH (Recommended):**

   ```powershell
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", [EnvironmentVariableTarget]::User)
   ```

   **Option B - Use direct path in CLI:**

   ```bash
   python -m yt_transcriber.cli -u "URL" --ffmpeg-location "C:\ffmpeg\bin\ffmpeg.exe"
   ```

4. **Verify installation:**
   ```powershell
   ffmpeg -version
   ```
   </details>

<details>
<summary><b>macOS Installation</b></summary>

```bash
# Using Homebrew
brew install ffmpeg

# Verify installation
ffmpeg -version
```

</details>

<details>
<summary><b>Linux Installation</b></summary>

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg

# Verify installation
ffmpeg -version
```

</details>

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/sergiomarquezdev/yt-video-summarizer.git
cd yt-video-summarizer

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create configuration file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Transcribe your first video!
python -m yt_transcriber.cli -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**For Developers:** Use `make setup` for automated environment configuration with modern tooling (UV, Ruff, Mypy). See [AGENTS.md](AGENTS.md) for details.

## 🌐 Web Interface (NEW)

The easiest way to use the tool is through the **Gradio web interface**:

```bash
# Launch web interface (auto-opens browser)
make start

# Or using direct command
uv run python frontend/gradio_app.py
```

The interface will open at **http://localhost:7860** with a two-column layout:

- **Left column**: Transcribe YouTube videos

  - Input URL, select language, customize FFmpeg path
  - View progress in real-time
  - Download transcription file

- **Right column**: Generate YouTube scripts
  - Input video idea and parameters
  - Adjust max videos, duration, and style
  - Download bilingual scripts (EN + ES)

**Why use the web interface?**

- ✅ No need to remember CLI commands
- ✅ User-friendly forms with validation
- ✅ Real-time progress indicators
- ✅ One-click file downloads
- ✅ Works in any browser

For detailed documentation, see [frontend/README.md](frontend/README.md).

---

## 💻 Usage

The tool provides two main commands:

### 1️⃣ Transcribe Videos

Transcribe YouTube videos to text files.

#### Basic Command

```bash
python -m yt_transcriber.cli transcribe --url "YOUTUBE_URL"
```

#### Command Options

| Option              | Short | Required | Description                                      |
| ------------------- | ----- | -------- | ------------------------------------------------ |
| `--url`             | `-u`  | ✅ Yes   | YouTube video URL                                |
| `--language`        | `-l`  | ❌ No    | Force specific language (e.g., `en`, `es`, `fr`) |
| `--ffmpeg-location` |       | ❌ No    | Custom FFmpeg path                               |

#### Examples

**Basic transcription (auto-detect language):**

```bash
python -m yt_transcriber.cli transcribe -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Force Spanish transcription:**

```bash
python -m yt_transcriber.cli transcribe -u "https://www.youtube.com/watch?v=VIDEO_ID" -l "es"
```

**With custom FFmpeg location:**

```bash
python -m yt_transcriber.cli transcribe -u "https://www.youtube.com/watch?v=VIDEO_ID" --ffmpeg-location "C:\ffmpeg\bin\ffmpeg.exe"
```

#### Output

After successful transcription, you'll see:

```
✅ Transcription saved: output_transcripts/VideoTitle_vid_VIDEO_ID_job_20231028123456.txt
```

Transcription files are saved in the `output_transcripts/` directory with a descriptive filename including:

- Video title
- Video ID
- Unique job timestamp

---

### 2️⃣ Generate Scripts (NEW)

Generate AI-powered YouTube scripts from successful videos in your niche.

#### Basic Command

```bash
python -m yt_transcriber.cli generate-script --idea "Your video idea"
```

#### Command Options

| Option           | Required | Default | Description                                          |
| ---------------- | -------- | ------- | ---------------------------------------------------- |
| `--idea`         | ✅ Yes   | -       | Your video idea or topic                             |
| `--max-videos`   | ❌ No    | 10      | Number of videos to analyze                          |
| `--duration`     | ❌ No    | 10      | Target duration in minutes                           |
| `--min-duration` | ❌ No    | 5       | Minimum video duration (minutes)                     |
| `--max-duration` | ❌ No    | 45      | Maximum video duration (minutes)                     |
| `--style`        | ❌ No    | -       | Optional style guide (e.g., "casual", "educational") |

#### Examples

**Generate a 10-minute Python tutorial script:**

```bash
python -m yt_transcriber.cli generate-script --idea "Python async/await tutorial"
```

**Quick 5-minute tutorial (analyze 5 videos):**

```bash
python -m yt_transcriber.cli generate-script \
  --idea "FastAPI REST API tutorial" \
  --max-videos 5 \
  --duration 5
```

**Educational video with casual style:**

```bash
python -m yt_transcriber.cli generate-script \
  --idea "Machine learning explained" \
  --duration 15 \
  --style "casual and entertaining" \
  --min-duration 10 \
  --max-duration 20
```

#### Output

The tool generates **bilingual scripts automatically** (English + Spanish):

```
📁 output_scripts/
  ├── 📄 {topic}_EN.md      # Original script in English
  └── 📄 {topic}_ES.md      # Translated script in Spanish

📁 output_analysis/
  └── 📄 {topic}_synthesis.md   # Pattern analysis report
```

**What you get (in BOTH languages):**

- ✅ **Complete script** with intro, body, and outro
- ✅ **SEO optimization** (title, description, tags)
- ✅ **Quality score** (1-100 based on structure and SEO)
- ✅ **Pattern analysis** from successful videos
- ✅ **Estimated duration** based on word count
- ✅ **Automatic Spanish translation** with technical term preservation

#### See More

For detailed documentation on the Script Generator, see [docs/YOUTUBE_SCRIPT_GENERATOR.md](docs/YOUTUBE_SCRIPT_GENERATOR.md).

---

### Help Commands

**See all transcribe options:**

```bash
python -m yt_transcriber.cli transcribe --help
```

**See all generate-script options:**

```bash
python -m yt_transcriber.cli generate-script --help
```

**See main help:**

```bash
python -m yt_transcriber.cli --help
```

## ⚙️ Configuration

Create a `.env` file in the project root to customize behavior:

```bash
# Whisper Model Configuration
WHISPER_MODEL_NAME=base          # Options: tiny, base, small, medium, large
WHISPER_DEVICE=cuda              # Options: cuda, cpu

# Logging
LOG_LEVEL=INFO                   # Options: DEBUG, INFO, WARNING, ERROR

# Directories (auto-created if missing)
TEMP_DOWNLOAD_DIR=temp_files/
OUTPUT_TRANSCRIPTS_DIR=output_transcripts/
```

### Model Selection Guide

| Model    | Speed      | Accuracy   | VRAM  | Use Case               |
| -------- | ---------- | ---------- | ----- | ---------------------- |
| `tiny`   | ⚡⚡⚡⚡⚡ | ⭐⭐       | ~1GB  | Quick drafts           |
| `base`   | ⚡⚡⚡⚡   | ⭐⭐⭐     | ~1GB  | **Default - Balanced** |
| `small`  | ⚡⚡⚡     | ⭐⭐⭐⭐   | ~2GB  | Good quality           |
| `medium` | ⚡⚡       | ⭐⭐⭐⭐⭐ | ~5GB  | High accuracy          |
| `large`  | ⚡         | ⭐⭐⭐⭐⭐ | ~10GB | Best quality           |

### Environment Variables Reference

| Variable                 | Default               | Description                         |
| ------------------------ | --------------------- | ----------------------------------- |
| `WHISPER_MODEL_NAME`     | `base`                | Whisper model size                  |
| `WHISPER_DEVICE`         | `cpu`                 | Processing device (`cpu` or `cuda`) |
| `TEMP_DOWNLOAD_DIR`      | `temp_files/`         | Temporary files location            |
| `OUTPUT_TRANSCRIPTS_DIR` | `output_transcripts/` | Output directory                    |
| `LOG_LEVEL`              | `INFO`                | Logging verbosity                   |

## 🔍 How It Works

1. **📥 Download**: Fetches the YouTube video using `yt-dlp`
2. **🎵 Extract**: Extracts audio from the video using FFmpeg
3. **🤖 Transcribe**: Processes audio with Whisper AI model
4. **💾 Save**: Saves transcription to `output_transcripts/`
5. **🧹 Cleanup**: Automatically removes temporary files

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>FFmpeg not found</b></summary>

**Solution 1: Verify installation**

```powershell
ffmpeg -version
```

**Solution 2: Use direct path**

```bash
python -m yt_transcriber.cli -u "URL" --ffmpeg-location "C:\ffmpeg\bin\ffmpeg.exe"
```

**Solution 3: Add to PATH (Windows)**

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", [EnvironmentVariableTarget]::User)
```

</details>

<details>
<summary><b>CUDA not available</b></summary>

If you have an NVIDIA GPU but CUDA isn't working:

1. **Check CUDA installation:**

   ```bash
   python test/check_pytorch_cuda.py
   ```

2. **Verify PyTorch CUDA support:**

   ```python
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. **Fall back to CPU:**
   Edit `.env`:
   ```bash
   WHISPER_DEVICE=cpu
   ```
   </details>

<details>
<summary><b>Out of memory errors</b></summary>

Use a smaller model in `.env`:

```bash
WHISPER_MODEL_NAME=tiny  # or base, small
```

</details>

<details>
<summary><b>Slow transcription</b></summary>

- Enable CUDA if you have an NVIDIA GPU
- Use a smaller model (`tiny` or `base`)
- Check system resources (RAM, CPU usage)
</details>

## 🧪 Development & Testing

This project follows modern Python best practices with comprehensive testing and code quality tools.

**Test Suite:**

- ✅ **49 integration tests** covering critical functionality
- ✅ **59% code coverage** (pragmatic and maintainable)
- ✅ **~6 second execution time** (fast feedback loop)
- ✅ **Zero linting/type errors** (Ruff + Mypy)

For detailed development setup and testing guidelines, see [AGENTS.md](AGENTS.md).

**Quick commands:**

```bash
# Setup development environment
make setup

# Run tests with coverage
make test-cov

# Run all quality checks (lint + format + typecheck + test)
make check

# See all available commands
make help
```

### Project Structure

```
yt-video-summarizer/
├── yt_transcriber/          # Main package
│   ├── cli.py              # CLI entry point
│   ├── config.py           # Configuration management
│   ├── downloader.py       # YouTube download logic
│   ├── transcriber.py      # Whisper transcription
│   └── utils.py            # Utilities
├── test/                    # Test suite
├── temp_files/             # Temporary storage (auto-cleaned)
├── output_transcripts/     # Transcription outputs
└── .env                    # Configuration (create from .env.example)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - AI model for transcription
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloader
- [PyTorch](https://pytorch.org/) - Deep learning framework

---

Made with ❤️ by [Sergio Márquez](https://github.com/sergiomarquezdev)
