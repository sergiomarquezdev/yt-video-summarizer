"""
Tests de integración End-to-End (E2E).

Estos tests prueban el flujo completo de la aplicación sin mocks pesados,
usando datos reales cuando es posible para detectar regresiones.
"""

from pathlib import Path

import pytest

from yt_transcriber import utils
from yt_transcriber.config import AppSettings


class TestUtilsIntegration:
    """Tests de integración para funciones de utilidad."""

    def test_ensure_dir_exists_creates_directory(self, tmp_path):
        """Test que ensure_dir_exists crea directorios correctamente."""
        new_dir = tmp_path / "new_directory"
        assert not new_dir.exists()

        utils.ensure_dir_exists(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_dir_exists_handles_existing_directory(self, tmp_path):
        """Test que ensure_dir_exists no falla si el directorio ya existe."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        assert existing_dir.exists()

        # No debería fallar
        utils.ensure_dir_exists(existing_dir)

        assert existing_dir.exists()

    def test_ensure_dir_exists_creates_nested_paths(self, tmp_path):
        """Test que ensure_dir_exists crea rutas anidadas."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        assert not nested_dir.exists()

        utils.ensure_dir_exists(nested_dir)

        assert nested_dir.exists()
        assert (tmp_path / "level1").exists()
        assert (tmp_path / "level1" / "level2").exists()

    def test_normalize_title_for_filename_removes_special_chars(self):
        """Test que normalize_title_for_filename elimina caracteres especiales."""
        dirty_name = "File/With\\Special:Chars*And?Emojis🎥"
        clean_name = utils.normalize_title_for_filename(dirty_name)

        # Verificar que no contiene caracteres prohibidos
        forbidden_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
        for char in forbidden_chars:
            assert char not in clean_name

    def test_normalize_title_for_filename_preserves_valid_chars(self):
        """Test que normalize_title_for_filename preserva caracteres válidos."""
        valid_name = "Valid_File-Name_123"
        clean_name = utils.normalize_title_for_filename(valid_name)

        assert "Valid" in clean_name
        assert "File" in clean_name
        assert "Name" in clean_name

    def test_normalize_title_for_filename_handles_empty_string(self):
        """Test que normalize_title_for_filename maneja strings vacíos."""
        result = utils.normalize_title_for_filename("")

        assert result == "untitled"

    def test_cleanup_temp_dir_removes_files(self, tmp_path):
        """Test que cleanup_temp_dir elimina archivos correctamente."""
        # Crear estructura de prueba
        temp_dir = tmp_path / "cleanup_test"
        temp_dir.mkdir()
        (temp_dir / "file1.txt").write_text("test")
        (temp_dir / "file2.wav").write_text("test")
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("test")

        assert temp_dir.exists()
        assert len(list(temp_dir.rglob("*"))) > 0

        # Limpiar
        utils.cleanup_temp_dir(temp_dir)

        # Verificar que se eliminó
        assert not temp_dir.exists()

    def test_cleanup_temp_dir_handles_non_existent(self, tmp_path):
        """Test que cleanup_temp_dir no falla si el directorio no existe."""
        non_existent = tmp_path / "does_not_exist"
        assert not non_existent.exists()

        # No debería lanzar error
        utils.cleanup_temp_dir(non_existent)

    def test_save_transcription_to_file_creates_file(self, temp_output_dir):
        """Test que save_transcription_to_file crea el archivo correctamente."""
        transcription_text = "This is a test transcription."
        video_title = "Test Video Title"
        filename_no_ext = "test_video_id_job123"

        output_path = utils.save_transcription_to_file(
            transcription_text=transcription_text,
            output_filename_no_ext=filename_no_ext,
            output_dir=temp_output_dir,
            original_title=video_title,
        )

        # Verificar que se creó el archivo
        assert output_path is not None
        assert output_path.exists()
        assert output_path.is_file()
        assert output_path.suffix == ".txt"

        # Verificar contenido
        content = output_path.read_text(encoding="utf-8")
        assert video_title in content
        assert transcription_text in content

    def test_cleanup_temp_files_removes_valid_files(self, tmp_path):
        """Test que cleanup_temp_files elimina archivos especificados."""
        file1 = tmp_path / "test1.txt"
        file2 = tmp_path / "test2.wav"
        file1.write_text("test")
        file2.write_text("test")

        assert file1.exists()
        assert file2.exists()

        utils.cleanup_temp_files([str(file1), str(file2)])

        assert not file1.exists()
        assert not file2.exists()

    def test_get_file_size_mb_returns_size(self, tmp_path):
        """Test que get_file_size_mb calcula correctamente el tamaño."""
        test_file = tmp_path / "test.txt"
        test_content = "x" * 1024 * 1024  # 1 MB
        test_file.write_text(test_content)

        size_mb = utils.get_file_size_mb(test_file)

        assert size_mb is not None
        assert size_mb >= 1.0  # Aproximadamente 1 MB


class TestConfigIntegration:
    """Tests de integración para la configuración."""

    def test_settings_can_be_instantiated(self):
        """Test que AppSettings se puede instanciar correctamente."""
        # Usar valores por defecto
        settings = AppSettings(
            WHISPER_MODEL_NAME="base",
            WHISPER_DEVICE="cpu",
            LOG_LEVEL="INFO",
            TEMP_DOWNLOAD_DIR="temp_files/",
            OUTPUT_TRANSCRIPTS_DIR="output_transcripts/",
        )

        assert settings.WHISPER_MODEL_NAME == "base"
        assert settings.WHISPER_DEVICE == "cpu"
        assert settings.LOG_LEVEL == "INFO"

    def test_settings_paths_are_path_objects(self):
        """Test que las rutas en AppSettings son objetos Path."""
        settings = AppSettings(
            WHISPER_MODEL_NAME="base",
            WHISPER_DEVICE="cpu",
            LOG_LEVEL="INFO",
            TEMP_DOWNLOAD_DIR="temp_files/",
            OUTPUT_TRANSCRIPTS_DIR="output_transcripts/",
        )

        assert isinstance(settings.TEMP_DOWNLOAD_DIR, Path)
        assert isinstance(settings.OUTPUT_TRANSCRIPTS_DIR, Path)


class TestCLIIntegration:
    """Tests de integración para el CLI (sin ejecutar comandos reales)."""

    def test_cli_module_can_be_imported(self):
        """Test que el módulo CLI se puede importar sin errores."""
        from yt_transcriber import cli

        assert hasattr(cli, "main")
        assert hasattr(cli, "load_whisper_model")
        assert hasattr(cli, "get_youtube_title")
        assert hasattr(cli, "process_transcription")


@pytest.mark.slow
class TestEndToEndWorkflow:
    """
    Tests E2E que simulan el flujo completo de la aplicación.

    Marcados como 'slow' porque requieren más tiempo de ejecución.
    Ejecutar con: pytest -m slow
    """

    def test_utils_workflow(self, temp_test_dir, temp_output_dir):
        """
        Test del flujo básico de utilidades: crear dir -> guardar archivo -> limpiar.
        """
        # Paso 1: Crear directorio
        utils.ensure_dir_exists(temp_test_dir)
        assert temp_test_dir.exists()

        # Paso 2: Crear archivo temporal
        temp_file = temp_test_dir / "test.wav"
        temp_file.write_bytes(b"FAKE_AUDIO")
        assert temp_file.exists()

        # Paso 3: Guardar transcripción
        transcription = "This is a test transcription."
        output_file = utils.save_transcription_to_file(
            transcription_text=transcription,
            output_filename_no_ext="test_video_job123",
            output_dir=temp_output_dir,
            original_title="Test Video",
        )

        assert output_file is not None
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "Test Video" in content
        assert transcription in content

        # Paso 4: Limpiar
        utils.cleanup_temp_dir(temp_test_dir)
        assert not temp_test_dir.exists()
