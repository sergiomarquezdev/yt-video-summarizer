# Módulo para transcribir archivos de audio usando Whisper

import dataclasses
import logging
import os

# from dataclasses import dataclass # Ya no se usa así, se usa import dataclasses y dataclasses.dataclass
# torch ya no es necesario aquí para la lógica principal, se usará en main.py para la carga
# import torch
import whisper  # whisper sigue siendo necesario para el tipo whisper.Whisper y DecodingOptions

# Configurar un logger simple para este módulo
logger = logging.getLogger(__name__)


# Modelo de datos para el resultado de la transcripción
@dataclasses.dataclass
class TranscriptionResult:
    text: str
    language: str | None = None


# Excepción personalizada para errores de transcripción
class TranscriptionError(Exception):
    pass


# Ya no se necesita la caché de modelo global aquí
# _loaded_model = None
# _loaded_model_name = None
# _loaded_model_device = None


def transcribe_audio_file(
    audio_path: str,
    model: whisper.Whisper,  # Acepta el modelo cargado
) -> TranscriptionResult:
    """
    Transcribe un archivo de audio utilizando el modelo Whisper proporcionado.

    Args:
        audio_path: Ruta al archivo de audio WAV.
        model: Instancia del modelo Whisper cargado.

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

    # La verificación de dispositivo y la carga del modelo ahora ocurren en main.py
    # if device == "cuda" and not torch.cuda.is_available():
    #     logger.warning("CUDA no está disponible. Cambiando a CPU.")
    #     device = "cpu"

    try:
        # El modelo ya está cargado y se pasa como argumento
        logger.info(f"Transcribiendo archivo: {audio_path}")
        options = whisper.DecodingOptions(
            language=None,  # language=None para auto-detección
            without_timestamps=True,
        )
        # Usar el modelo proporcionado
        result = model.transcribe(audio_path, **dataclasses.asdict(options))

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
            detected_language = None

        logger.info(
            f"Transcripción completada. Idioma detectado: {detected_language}. Longitud: {len(transcribed_text)} chars."
        )
        return TranscriptionResult(text=transcribed_text, language=detected_language)

    except FileNotFoundError:  # Aunque os.path.exists lo cubre, por si acaso.
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
        # Ya no se invalida el modelo aquí, la gestión es externa.
        # _loaded_model = None
        raise TranscriptionError(f"Error inesperado en Whisper: {e}")


if __name__ == "__main__":
    # El bloque de prueba __main__ ha cambiado significativamente debido a que
    # la carga del modelo Whisper ahora es externa (manejada por main.py).
    # Para probar este módulo de forma aislada, necesitarías cargar manualmente
    # un modelo Whisper y pasarlo a la función transcribe_audio_file.

    logger.info("--- Bloque de prueba __main__ de transcriber.py ---")
    logger.warning("Funcionalidad de prueba directa de este módulo ha cambiado.")
    logger.warning(
        "Modelo Whisper ahora se carga en la aplicación principal (main.py)."
    )
    logger.info("Para probar transcribe_audio_file aisladamente:")
    logger.info(
        "  1. Asegúrate de tener un archivo WAV de prueba (ej. 'test_audio_sample.wav')."
    )
    logger.info("  2. Carga manualmente un modelo Whisper en este script.")
    logger.info("  3. Pasa la instancia del modelo y la ruta del audio a la función.")
    logger.info("Ejemplo conceptual de cómo probarlo:")
    logger.info("  # import whisper")
    logger.info("  # import os")
    logger.info("  # test_model_instance = whisper.load_model('tiny', device='cpu')")
    logger.info(
        "  # audio_file = 'test_audio_sample.wav' # Asegúrate que exista o créalo"
    )
    logger.info("  # if os.path.exists(audio_file):")
    logger.info(
        '  #     try:\n        #         transcription = transcribe_audio_file(audio_file, test_model_instance)\n        #         if transcription:\n        #             print(f"Transcripción: {transcription.text}")\n        #     except TranscriptionError as e_script:\n        #         print(f"Error en prueba: {e_script}")\n        # else:\n        #     print(f"Archivo de audio de prueba \'{audio_file}\' no encontrado.\')'
    )
