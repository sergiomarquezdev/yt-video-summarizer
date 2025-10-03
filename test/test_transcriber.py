"""
Tests de integración para el módulo transcriber.

Prueba la funcionalidad de transcripción con archivos de audio reales (pequeños).
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from yt_transcriber.transcriber import (
    TranscriptionError,
    TranscriptionResult,
    transcribe_audio_file,
)


class TestTranscriberIntegration:
    """Tests de integración para el transcriber."""

    def test_transcription_result_dataclass(self):
        """Test que TranscriptionResult se puede crear correctamente."""
        result = TranscriptionResult(text="Test transcription", language="en")

        assert result.text == "Test transcription"
        assert result.language == "en"

    def test_transcription_result_optional_language(self):
        """Test que language es opcional en TranscriptionResult."""
        result = TranscriptionResult(text="Test transcription")

        assert result.text == "Test transcription"
        assert result.language is None

    def test_transcription_error_exception(self):
        """Test que TranscriptionError se puede lanzar y capturar."""
        with pytest.raises(TranscriptionError, match="Test transcription error"):
            raise TranscriptionError("Test transcription error")

    def test_transcribe_audio_file_not_found(self, mock_whisper_model):
        """Test que se lanza error cuando el archivo de audio no existe."""
        non_existent_path = Path("/fake/non_existent_audio.wav")

        with pytest.raises(TranscriptionError, match="Archivo de audio no encontrado"):
            transcribe_audio_file(
                audio_path=non_existent_path,
                model=mock_whisper_model,
                language=None,
            )

    def test_transcribe_audio_file_success(
        self, temp_test_dir, mock_whisper_model, sample_transcription_result
    ):
        """Test de transcripción exitosa con archivo válido."""
        # Crear archivo de audio de prueba (vacío está bien para este test)
        audio_path = temp_test_dir / "test_audio.wav"
        audio_path.write_bytes(b"FAKE_WAV_CONTENT")

        # Configurar mock del modelo
        mock_whisper_model.transcribe.return_value = sample_transcription_result
        mock_whisper_model.device = Mock()
        mock_whisper_model.device.type = "cpu"

        # Ejecutar transcripción
        result = transcribe_audio_file(
            audio_path=audio_path, model=mock_whisper_model, language=None
        )

        # Verificar resultado
        assert isinstance(result, TranscriptionResult)
        assert result.text == sample_transcription_result["text"]
        assert result.language == sample_transcription_result["language"]

        # Verificar que se llamó al modelo correctamente
        mock_whisper_model.transcribe.assert_called_once()
        call_args = mock_whisper_model.transcribe.call_args
        assert str(audio_path) in call_args[0]

    def test_transcribe_audio_file_with_language(
        self, temp_test_dir, mock_whisper_model, sample_transcription_result
    ):
        """Test de transcripción con idioma especificado."""
        audio_path = temp_test_dir / "test_audio_es.wav"
        audio_path.write_bytes(b"FAKE_WAV_CONTENT")

        # Modificar resultado para español
        spanish_result = sample_transcription_result.copy()
        spanish_result["language"] = "es"
        mock_whisper_model.transcribe.return_value = spanish_result
        mock_whisper_model.device = Mock()
        mock_whisper_model.device.type = "cpu"

        # Ejecutar con idioma español
        result = transcribe_audio_file(
            audio_path=audio_path, model=mock_whisper_model, language="es"
        )

        assert result.language == "es"

        # Verificar que se pasó el parámetro de idioma
        call_kwargs = mock_whisper_model.transcribe.call_args[1]
        assert call_kwargs["language"] == "es"

    def test_transcribe_audio_file_cuda_fp16(self, temp_test_dir, sample_transcription_result):
        """Test que se usa fp16 cuando el modelo está en CUDA."""
        audio_path = temp_test_dir / "test_audio_cuda.wav"
        audio_path.write_bytes(b"FAKE_WAV_CONTENT")

        # Mock modelo CUDA
        mock_cuda_model = Mock()
        mock_cuda_model.device = Mock()
        mock_cuda_model.device.type = "cuda"
        mock_cuda_model.transcribe.return_value = sample_transcription_result

        # Ejecutar transcripción
        result = transcribe_audio_file(audio_path=audio_path, model=mock_cuda_model, language=None)

        assert isinstance(result, TranscriptionResult)

        # Verificar que se pasó fp16=True para CUDA
        call_kwargs = mock_cuda_model.transcribe.call_args[1]
        assert call_kwargs["fp16"] is True

    def test_transcribe_audio_file_cpu_no_fp16(self, temp_test_dir, sample_transcription_result):
        """Test que NO se usa fp16 cuando el modelo está en CPU."""
        audio_path = temp_test_dir / "test_audio_cpu.wav"
        audio_path.write_bytes(b"FAKE_WAV_CONTENT")

        # Mock modelo CPU
        mock_cpu_model = Mock()
        mock_cpu_model.device = Mock()
        mock_cpu_model.device.type = "cpu"
        mock_cpu_model.transcribe.return_value = sample_transcription_result

        # Ejecutar transcripción
        transcribe_audio_file(audio_path=audio_path, model=mock_cpu_model, language=None)

        # Verificar que se pasó fp16=False para CPU
        call_kwargs = mock_cpu_model.transcribe.call_args[1]
        assert call_kwargs["fp16"] is False

    def test_transcribe_audio_file_empty_text_warning(
        self, temp_test_dir, caplog, mock_whisper_model
    ):
        """Test que se registra warning cuando la transcripción está vacía."""
        audio_path = temp_test_dir / "silent_audio.wav"
        audio_path.write_bytes(b"FAKE_WAV_CONTENT")

        # Simular transcripción vacía
        empty_result = {"text": "", "language": "en"}
        mock_whisper_model.transcribe.return_value = empty_result
        mock_whisper_model.device = Mock()
        mock_whisper_model.device.type = "cpu"

        # Ejecutar transcripción
        result = transcribe_audio_file(
            audio_path=audio_path, model=mock_whisper_model, language=None
        )

        # Verificar que devuelve texto vacío sin error
        assert result.text == ""
        assert result.language == "en"

        # Verificar que se registró el warning
        assert any(
            "La transcripción ha devuelto un texto vacío" in record.message
            for record in caplog.records
        )

    def test_transcribe_audio_file_whisper_exception(self, temp_test_dir, mock_whisper_model):
        """Test que se maneja correctamente cuando Whisper falla."""
        audio_path = temp_test_dir / "corrupt_audio.wav"
        audio_path.write_bytes(b"CORRUPTED_DATA")

        # Simular error de Whisper
        mock_whisper_model.transcribe.side_effect = RuntimeError("Whisper processing error")
        mock_whisper_model.device = Mock()
        mock_whisper_model.device.type = "cpu"

        with pytest.raises(TranscriptionError, match="Error inesperado en Whisper"):
            transcribe_audio_file(audio_path=audio_path, model=mock_whisper_model, language=None)
