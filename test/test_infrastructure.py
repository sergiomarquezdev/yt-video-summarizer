"""
Sanity check tests to verify pytest infrastructure is working.

These tests should always pass and verify that our test setup is correct.
"""

import pytest


class TestPytestInfrastructure:
    """Verify that pytest infrastructure is set up correctly."""

    def test_pytest_is_working(self):
        """Sanity check: pytest is running."""
        assert True

    def test_fixtures_available(self, tmp_path):
        """Verify that pytest fixtures are available."""
        assert tmp_path.exists()
        assert tmp_path.is_dir()

    def test_can_create_files(self, tmp_path):
        """Verify that we can create test files."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        assert test_file.exists()
        assert test_file.read_text() == "Hello, World!"


class TestCustomFixtures:
    """Verify that our custom fixtures work correctly."""

    def test_temp_test_dir_fixture(self, temp_test_dir):
        """Verify temp_test_dir fixture works."""
        assert temp_test_dir.exists()
        assert temp_test_dir.is_dir()

    def test_temp_output_dir_fixture(self, temp_output_dir):
        """Verify temp_output_dir fixture works."""
        assert temp_output_dir.exists()
        assert temp_output_dir.is_dir()

    def test_sample_youtube_url_fixture(self, sample_youtube_url):
        """Verify sample_youtube_url fixture provides valid URL."""
        assert isinstance(sample_youtube_url, str)
        assert sample_youtube_url.startswith("https://www.youtube.com/")

    def test_sample_video_id_fixture(self, sample_video_id):
        """Verify sample_video_id fixture provides valid ID."""
        assert isinstance(sample_video_id, str)
        assert len(sample_video_id) == 11  # YouTube video IDs are 11 chars

    def test_sample_video_info_fixture(self, sample_video_info):
        """Verify sample_video_info fixture has required fields."""
        assert "id" in sample_video_info
        assert "title" in sample_video_info
        assert "duration" in sample_video_info

    def test_sample_transcription_result_fixture(self, sample_transcription_result):
        """Verify sample_transcription_result fixture has required fields."""
        assert "text" in sample_transcription_result
        assert "language" in sample_transcription_result
        assert isinstance(sample_transcription_result["text"], str)

    def test_sample_audio_path_fixture(self, sample_audio_path):
        """Verify sample_audio_path fixture creates a file."""
        assert sample_audio_path.exists()
        assert sample_audio_path.is_file()


class TestMockFixtures:
    """Verify that mock fixtures are working."""

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("yt_dlp"),
        reason="yt_dlp not installed",
    )
    def test_mock_ytdl_fixture(self, mock_ytdl, sample_video_info):
        """Verify mock_ytdl fixture is configured correctly."""
        result = mock_ytdl.extract_info("fake_url", download=False)
        assert result == sample_video_info
        mock_ytdl.extract_info.assert_called_once()

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("whisper"),
        reason="whisper not installed",
    )
    def test_mock_whisper_model_fixture(self, mock_whisper_model, sample_transcription_result):
        """Verify mock_whisper_model fixture is configured correctly."""
        result = mock_whisper_model.transcribe("fake_audio.wav")
        assert result == sample_transcription_result
        assert mock_whisper_model.device.type == "cpu"

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("whisper"),
        reason="whisper not installed",
    )
    def test_mock_whisper_model_cuda_fixture(self, mock_whisper_model_cuda):
        """Verify mock_whisper_model_cuda fixture is configured for CUDA."""
        assert mock_whisper_model_cuda.device.type == "cuda"

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("torch"),
        reason="torch not installed",
    )
    def test_mock_cuda_available_fixture(self, mock_cuda_available, mocker):
        """Verify mock_cuda_available fixture mocks CUDA correctly."""
        import torch

        assert torch.cuda.is_available() is True

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("torch"),
        reason="torch not installed",
    )
    def test_mock_cuda_unavailable_fixture(self, mock_cuda_unavailable, mocker):
        """Verify mock_cuda_unavailable fixture mocks CUDA correctly."""
        import torch

        assert torch.cuda.is_available() is False


@pytest.mark.parametrize(
    "value,expected",
    [
        (1 + 1, 2),
        (2 * 2, 4),
        (3 - 1, 2),
    ],
)
def test_parametrize_works(value, expected):
    """Verify that pytest parametrize works."""
    assert value == expected
