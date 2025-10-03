"""
Pytest configuration and shared fixtures for YouTube Transcriber tests.

This file contains common fixtures and configuration used across all tests.
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest


# ============================================================================
# Fixture: Temporary Directories
# ============================================================================


@pytest.fixture
def temp_test_dir(tmp_path) -> Path:
    """
    Provide a temporary directory for test files.
    Automatically cleaned up after test.
    """
    test_dir = tmp_path / "test_temp"
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup happens automatically via tmp_path


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """
    Provide a temporary directory for test output files.
    """
    output_dir = tmp_path / "test_output"
    output_dir.mkdir(exist_ok=True)
    yield output_dir


# ============================================================================
# Fixture: Sample YouTube Video Data
# ============================================================================


@pytest.fixture
def sample_youtube_url() -> str:
    """Provide a sample YouTube URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def sample_video_id() -> str:
    """Provide a sample YouTube video ID."""
    return "dQw4w9WgXcQ"


@pytest.fixture
def sample_video_info() -> dict[str, Any]:
    """
    Provide sample video info as returned by yt-dlp.

    This mimics the structure returned by yt_dlp.YoutubeDL.extract_info()
    """
    return {
        "id": "dQw4w9WgXcQ",
        "title": "Sample Test Video Title",
        "description": "This is a test video description",
        "duration": 212,  # 3:32 in seconds
        "uploader": "Test Channel",
        "upload_date": "20091025",
        "view_count": 1000000,
        "like_count": 50000,
        "ext": "mp4",
        "format": "bestaudio/best",
    }


@pytest.fixture
def sample_video_info_with_special_chars() -> dict[str, Any]:
    """Video info with special characters in title for sanitization testing."""
    return {
        "id": "test123",
        "title": "Test Video: With/Special\\Chars & Emojis 🎥📝",
        "description": "Test description",
        "duration": 60,
    }


# ============================================================================
# Fixture: Mock yt-dlp
# ============================================================================


@pytest.fixture
def mock_ytdl(mocker, sample_video_info):
    """
    Mock yt_dlp.YoutubeDL for testing without network calls.

    Usage:
        def test_something(mock_ytdl):
            # mock_ytdl is already configured
            result = download_function()
    """
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.return_value = sample_video_info
    mock_ytdl_instance.prepare_filename.return_value = "/fake/path/video.mp4"

    # Mock the context manager
    mock_ytdl_class = mocker.patch("yt_dlp.YoutubeDL")
    mock_ytdl_class.return_value.__enter__.return_value = mock_ytdl_instance
    mock_ytdl_class.return_value.__exit__.return_value = None

    return mock_ytdl_instance


# ============================================================================
# Fixture: Mock Whisper
# ============================================================================


@pytest.fixture
def sample_transcription_result() -> dict[str, Any]:
    """Sample transcription result as returned by Whisper."""
    return {
        "text": "This is a sample transcription text from the video.",
        "language": "en",
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 5.0,
                "text": "This is a sample transcription",
            },
            {
                "id": 1,
                "start": 5.0,
                "end": 10.0,
                "text": " text from the video.",
            },
        ],
    }


@pytest.fixture
def mock_whisper_model(mocker, sample_transcription_result):
    """
    Mock Whisper model for testing without loading actual model.

    Usage:
        def test_transcription(mock_whisper_model):
            # model is already mocked
            result = transcribe_function()
    """
    mock_model = Mock()
    mock_model.transcribe.return_value = sample_transcription_result
    mock_model.device.type = "cpu"  # Default to CPU for tests

    # Mock the load_model function
    mocker.patch("whisper.load_model", return_value=mock_model)

    return mock_model


@pytest.fixture
def mock_whisper_model_cuda(mocker, sample_transcription_result):
    """Mock Whisper model configured for CUDA."""
    mock_model = Mock()
    mock_model.transcribe.return_value = sample_transcription_result
    mock_model.device.type = "cuda"

    mocker.patch("whisper.load_model", return_value=mock_model)

    return mock_model


# ============================================================================
# Fixture: Mock torch.cuda
# ============================================================================


@pytest.fixture
def mock_cuda_available(mocker):
    """Mock CUDA as available for testing GPU code paths."""
    mocker.patch("torch.cuda.is_available", return_value=True)
    mocker.patch("torch.cuda.get_device_name", return_value="NVIDIA GeForce RTX 3060")


@pytest.fixture
def mock_cuda_unavailable(mocker):
    """Mock CUDA as unavailable for testing CPU fallback."""
    mocker.patch("torch.cuda.is_available", return_value=False)


# ============================================================================
# Fixture: Sample Audio Files
# ============================================================================


@pytest.fixture
def sample_audio_path(tmp_path) -> Path:
    """
    Create a dummy audio file for testing.
    Note: This is an empty file, sufficient for most tests.
    """
    audio_file = tmp_path / "sample_audio.wav"
    audio_file.write_bytes(b"RIFF....WAV")  # Minimal WAV header
    return audio_file


# ============================================================================
# Fixture: Mock Environment Variables
# ============================================================================


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Mock environment variables for testing configuration.

    Usage:
        def test_config(mock_env_vars):
            mock_env_vars({'WHISPER_MODEL_NAME': 'small'})
    """

    def _set_env_vars(env_dict: dict[str, str]):
        for key, value in env_dict.items():
            monkeypatch.setenv(key, value)

    return _set_env_vars


# ============================================================================
# Fixture: Clean Test Environment
# ============================================================================


@pytest.fixture(autouse=True)
def clean_test_env(tmp_path, monkeypatch):
    """
    Automatically clean test environment for each test.

    This fixture runs automatically for all tests (autouse=True).
    """
    # Set temporary directories for tests
    monkeypatch.setenv("TEMP_DOWNLOAD_DIR", str(tmp_path / "temp_files"))
    monkeypatch.setenv("OUTPUT_TRANSCRIPTS_DIR", str(tmp_path / "output"))

    yield

    # Cleanup is handled by tmp_path automatically


# ============================================================================
# Helper Functions
# ============================================================================


def create_mock_audio_file(path: Path, size_kb: int = 10):
    """
    Helper function to create a mock audio file with specified size.

    Args:
        path: Path where to create the file
        size_kb: Size of file in kilobytes
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"0" * (size_kb * 1024))


def create_mock_video_file(path: Path, size_kb: int = 100):
    """
    Helper function to create a mock video file with specified size.

    Args:
        path: Path where to create the file
        size_kb: Size of file in kilobytes
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"0" * (size_kb * 1024))
