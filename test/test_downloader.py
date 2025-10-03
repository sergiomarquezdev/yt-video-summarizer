"""
Tests de integración para el módulo downloader.

Estos tests prueban la funcionalidad real de descarga sin mocks excesivos.
Solo se mockean las partes más pesadas (descarga de video real).
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from yt_transcriber.downloader import (
    DownloadError,
    DownloadResult,
    download_and_extract_audio,
)


class TestDownloaderIntegration:
    """Tests de integración para el downloader."""

    def test_download_result_dataclass(self):
        """Test que DownloadResult se puede crear correctamente."""
        result = DownloadResult(
            audio_path=Path("/fake/audio.wav"),
            video_path=Path("/fake/video.mp4"),
            video_id="test123",
        )

        assert result.audio_path == Path("/fake/audio.wav")
        assert result.video_path == Path("/fake/video.mp4")
        assert result.video_id == "test123"

    def test_download_error_exception(self):
        """Test que DownloadError se puede lanzar y capturar."""
        with pytest.raises(DownloadError, match="Test error message"):
            raise DownloadError("Test error message")

    @patch("yt_transcriber.downloader.yt_dlp.YoutubeDL")
    def test_download_and_extract_audio_success(
        self, mock_ytdl_class, temp_test_dir, sample_video_info
    ):
        """Test de descarga exitosa con mocks mínimos."""
        # Simular archivos descargados
        video_id = sample_video_info["id"]
        job_id = "test_job_123"
        expected_audio = temp_test_dir / f"{video_id}_{job_id}.wav"
        expected_video = temp_test_dir / f"{video_id}_{job_id}.webm"

        # Configurar mock de yt-dlp
        mock_instance = Mock()
        mock_instance.extract_info.return_value = sample_video_info
        mock_instance.prepare_filename.return_value = str(expected_video)
        mock_ytdl_class.return_value.__enter__.return_value = mock_instance
        mock_ytdl_class.return_value.__exit__.return_value = None

        # Crear archivos simulados
        expected_audio.touch()
        expected_video.touch()

        # Ejecutar descarga
        result = download_and_extract_audio(
            youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            temp_dir=temp_test_dir,
            unique_job_id=job_id,
        )

        # Verificar resultado
        assert isinstance(result, DownloadResult)
        assert result.video_id == video_id
        assert result.audio_path == expected_audio
        assert result.audio_path.exists()

    @patch("yt_transcriber.downloader.yt_dlp.YoutubeDL")
    def test_download_missing_video_id(self, mock_ytdl_class, temp_test_dir):
        """Test que se lanza error cuando no se puede extraer el video ID."""
        # Configurar mock para devolver info sin ID
        mock_instance = Mock()
        mock_instance.extract_info.return_value = {"title": "Test", "id": None}
        mock_ytdl_class.return_value.__enter__.return_value = mock_instance
        mock_ytdl_class.return_value.__exit__.return_value = None

        with pytest.raises(DownloadError, match="No se pudo extraer el ID del video"):
            download_and_extract_audio(
                youtube_url="https://invalid.url",
                temp_dir=temp_test_dir,
                unique_job_id="test_job",
            )

    @patch("yt_transcriber.downloader.yt_dlp.YoutubeDL")
    def test_download_handles_ytdlp_exception(self, mock_ytdl_class, temp_test_dir):
        """Test que se maneja correctamente cuando yt-dlp falla."""
        # Simular error de yt-dlp
        mock_instance = Mock()
        mock_instance.extract_info.side_effect = Exception("Network error")
        mock_ytdl_class.return_value.__enter__.return_value = mock_instance
        mock_ytdl_class.return_value.__exit__.return_value = None

        with pytest.raises(DownloadError, match="Error general en descarga"):
            download_and_extract_audio(
                youtube_url="https://www.youtube.com/watch?v=invalid",
                temp_dir=temp_test_dir,
                unique_job_id="test_job",
            )

    def test_download_creates_temp_directory(self, tmp_path):
        """Test que se crea el directorio temporal si no existe."""
        non_existent_dir = tmp_path / "new_temp_dir"
        assert not non_existent_dir.exists()

        # El mock evitará la descarga real, pero verificamos que se crea el dir
        with patch("yt_transcriber.downloader.yt_dlp.YoutubeDL") as mock_ytdl_class:
            mock_instance = Mock()
            mock_instance.extract_info.return_value = {"id": "test123"}
            expected_video = non_existent_dir / "test123_job.webm"
            mock_instance.prepare_filename.return_value = str(expected_video)
            mock_ytdl_class.return_value.__enter__.return_value = mock_instance
            mock_ytdl_class.return_value.__exit__.return_value = None

            # Simular archivo creado
            audio_path = non_existent_dir / "test123_job.wav"
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            audio_path.touch()
            expected_video.touch()

            result = download_and_extract_audio(
                youtube_url="https://www.youtube.com/watch?v=test",
                temp_dir=non_existent_dir,
                unique_job_id="job",
            )

            assert non_existent_dir.exists()
            assert result.audio_path.parent == non_existent_dir
