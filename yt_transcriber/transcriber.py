# Módulo para transcribir archivos de audio usando Whisper
import dataclasses
import logging
from pathlib import Path

import whisper


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TranscriptionResult:
    """Contiene el resultado de una transcripción."""

    text: str
    language: str | None = None


class TranscriptionError(Exception):
    """Excepción personalizada para errores de transcripción."""

    pass


def transcribe_audio_file(
    audio_path: Path,
    model: whisper.Whisper,
    language: str | None = None,
) -> TranscriptionResult:
    """
    Transcribe un archivo de audio utilizando el modelo Whisper proporcionado.

    Args:
        audio_path: Ruta al archivo de audio WAV.
        model: Instancia del modelo Whisper cargado.
        language: Código de idioma opcional para forzar la transcripción (ej. "en", "es").
                  Si es None, Whisper auto-detectará el idioma.

    Returns:
        Un objeto TranscriptionResult con el texto y el idioma detectado.

    Raises:
        TranscriptionError: Si el archivo no existe o si ocurre un error en Whisper.
    """
    logger.info(f"Iniciando transcripción para: {audio_path} usando modelo Whisper pre-cargado.")

    if not audio_path.exists():
        logger.error(f"Error de transcripción: Archivo de audio no encontrado en {audio_path}")
        raise TranscriptionError(f"Archivo de audio no encontrado: {audio_path}")

    try:
        logger.info(f"Transcribiendo archivo: {audio_path} con idioma='{language}'")

        transcribe_options = {"fp16": model.device.type == "cuda"}
        if language:
            transcribe_options["language"] = language

        result = model.transcribe(str(audio_path), **transcribe_options)

        transcribed_text = result.get("text", "").strip()
        if not transcribed_text:
            logger.warning("La transcripción ha devuelto un texto vacío.")
            # No se lanza error, puede ser un audio silencioso.

        detected_language = result.get("language")

        logger.info(
            f"Transcripción completada. Idioma detectado: {detected_language}. Longitud: {len(transcribed_text)} chars."
        )
        return TranscriptionResult(text=transcribed_text, language=detected_language)

    except Exception as e:
        logger.error(
            f"Error inesperado durante transcripción de '{audio_path}': {e}",
            exc_info=True,
        )
        raise TranscriptionError(f"Error inesperado en Whisper: {e}") from e
