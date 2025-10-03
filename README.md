# 🎥 YouTube Video Transcriber

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%2012.8-red.svg)](https://pytorch.org/)

A powerful CLI tool to download YouTube videos and transcribe them to text using [OpenAI's Whisper](https://github.com/openai/whisper) model. Supports CUDA acceleration for faster transcription and automatic language detection.

## ✨ Features

- 🚀 **Fast transcription** with CUDA GPU acceleration support
- 🌍 **Multi-language support** with automatic language detection
- 📝 **High accuracy** using OpenAI's Whisper models (tiny to large)
- 🎯 **Simple CLI interface** with minimal configuration
- 🔄 **Automatic cleanup** of temporary files
- 📊 **Multiple model sizes** to balance speed vs accuracy

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
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

## 💻 Usage

### Basic Command

```bash
python -m yt_transcriber.cli --url "YOUTUBE_URL"
```

### Command Options

| Option              | Short | Required | Description                                      |
| ------------------- | ----- | -------- | ------------------------------------------------ |
| `--url`             | `-u`  | ✅ Yes   | YouTube video URL                                |
| `--language`        | `-l`  | ❌ No    | Force specific language (e.g., `en`, `es`, `fr`) |
| `--ffmpeg-location` |       | ❌ No    | Custom FFmpeg path                               |

### Examples

**Basic transcription (auto-detect language):**

```bash
python -m yt_transcriber.cli -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Force Spanish transcription:**

```bash
python -m yt_transcriber.cli -u "https://www.youtube.com/watch?v=VIDEO_ID" -l "es"
```

**With custom FFmpeg location:**

```bash
python -m yt_transcriber.cli -u "https://www.youtube.com/watch?v=VIDEO_ID" --ffmpeg-location "C:\ffmpeg\bin\ffmpeg.exe"
```

**See all options:**

```bash
python -m yt_transcriber.cli --help
```

### Output

After successful transcription, you'll see:

```
✅ Transcription saved: output_transcripts/VideoTitle_vid_VIDEO_ID_job_20231028123456.txt
```

Transcription files are saved in the `output_transcripts/` directory with a descriptive filename including:

- Video title
- Video ID
- Unique job timestamp

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

For development setup and testing guidelines, see [AGENTS.md](AGENTS.md).

**Quick commands:**

```bash
# Setup development environment
make setup

# Run tests
make test

# Run all quality checks
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
