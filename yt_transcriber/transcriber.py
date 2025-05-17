# Módulo para transcribir archivos de audio usando Whisper

import dataclasses
import logging
import os
from typing import Optional

import whisper  # Requerido para el type hint whisper.Whisper

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TranscriptionResult:
    text: str
    language: str | None = None


class TranscriptionError(Exception):
    pass


def transcribe_audio_file(
    audio_path: str,
    model: whisper.Whisper,  # Acepta el modelo cargado
    language: Optional[str] = None,
    include_timestamps: bool = False,
) -> TranscriptionResult:
    """
    Transcribe un archivo de audio utilizando el modelo Whisper proporcionado.

    Args:
        audio_path: Ruta al archivo de audio WAV.
        model: Instancia del modelo Whisper cargado.
        language: Código de idioma opcional para forzar la transcripción (ej. "en", "es").
                  Si es None, Whisper auto-detectará el idioma.
        include_timestamps: Si es True, se pedirán timestamps a Whisper.

    Returns:
        Un objeto TranscriptionResult con el texto y el idioma detectado.

    Raises:
        TranscriptionError: Si ocurre un error durante la transcripción.
    """
    logger.info(
        f"Iniciando transcripción para: {audio_path} usando modelo Whisper pre-cargado."
    )

    if not os.path.exists(audio_path):
        logger.error(
            f"Error de transcripción: Archivo de audio no encontrado en {audio_path}"
        )
        raise TranscriptionError(f"Archivo de audio no encontrado: {audio_path}")

    try:
        logger.info(
            f"Transcribiendo archivo: {audio_path} con idioma='{language}', include_timestamps={include_timestamps}"
        )

        transcribe_options = {}
        if language:
            transcribe_options["language"] = language

        transcribe_options["without_timestamps"] = not include_timestamps

        # Nota: La opción fp16 puede considerarse para GPUs compatibles.
        # Ejemplo:
        # if model.device.type == "cuda":
        #     transcribe_options["fp16"] = True

        result = model.transcribe(audio_path, **transcribe_options)

        transcribed_text = result.get("text")
        detected_language = result.get("language")

        if not isinstance(transcribed_text, str):
            logger.error(
                f"El resultado de la transcripción para 'text' no es un string: {type(transcribed_text)}"
            )
            raise TranscriptionError("Formato de texto de transcripción inesperado.")

        if detected_language is not None and not isinstance(detected_language, str):
            logger.warning(
                f"El idioma detectado no es un string (valor: {detected_language}). Se tratará como None."
            )
            detected_language = None  # Asegurar que sea None si no es un string válido

        logger.info(
            f"Transcripción completada. Idioma detectado: {detected_language}. Longitud: {len(transcribed_text)} chars."
        )
        return TranscriptionResult(text=transcribed_text, language=detected_language)

    except FileNotFoundError:
        logger.error(
            f"Error de transcripción (FileNotFound): Archivo de audio no encontrado en {audio_path}"
        )
        raise TranscriptionError(
            f"Archivo de audio no encontrado durante operación Whisper: {audio_path}"
        )
    except Exception as e:
        logger.error(
            f"Error inesperado durante transcripción de '{audio_path}': {e}",
            exc_info=True,
        )
        raise TranscriptionError(f"Error inesperado en Whisper: {e}")
