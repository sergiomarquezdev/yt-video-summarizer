import argparse
import logging
import os
import sys
import threading
import time
from datetime import datetime

from yt_transcriber import config, downloader, transcriber, utils
from yt_transcriber.downloader import DownloadError
from yt_transcriber.transcriber import TranscriptionError, TranscriptionResult

# Configuración del logger (similar a como estaba en main.py pero simplificado para CLI)
logger = logging.getLogger(__name__)
numeric_log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=numeric_log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Variable global para el modelo Whisper y su dispositivo (simulando app.state)
# Esto es opcional para un CLI simple, el modelo podría cargarse siempre.
# Pero para mantener la lógica del Transcriber, lo precargaremos si es posible.
_whisper_model_instance = None
_whisper_device_used = "cpu"  # Default


def load_whisper_model_globally():
    """Carga el modelo Whisper globalmente, similar al evento startup de FastAPI."""
    global _whisper_model_instance, _whisper_device_used

    if _whisper_model_instance is not None:
        # logger.info("Modelo Whisper ya cargado.") # Puede ser muy verboso
        return

    logger.info("Cargando modelo Whisper...")
    device_to_use = config.WHISPER_DEVICE

    # Intentar importar torch y whisper aquí para evitar importarlos si no se usa la función.
    try:
        import torch
        import whisper
    except ImportError as e:
        logger.critical(
            f"No se pudieron importar torch o whisper. Asegúrate de que estén instalados. Error: {e}"
        )
        sys.exit(1)  # Salir si las dependencias críticas no están

    if device_to_use == "cuda" and not torch.cuda.is_available():
        logger.warning(
            "CUDA no disponible según torch.cuda.is_available(). Cambiando a CPU para Whisper."
        )
        device_to_use = "cpu"

    try:
        model = whisper.load_model(config.WHISPER_MODEL_NAME, device=device_to_use)
        _whisper_model_instance = model
        _whisper_device_used = device_to_use
        logger.info(
            f"Modelo Whisper '{config.WHISPER_MODEL_NAME}' cargado exitosamente en '{device_to_use}'."
        )
    except Exception as e:
        logger.critical(
            f"Fallo CRÍTICO al cargar modelo Whisper '{config.WHISPER_MODEL_NAME}' en '{device_to_use}'. Error: {e}",
            exc_info=True,
        )
        sys.exit(1)  # Salir si el modelo no se puede cargar


def log_heartbeat(interval_seconds: int, stop_event: threading.Event):
    """
    Función para loguear un mensaje periódico mientras no se activa el evento de parada.
    """
    logger.info("Iniciando heartbeat de transcripción...")
    start_time = time.time()
    while not stop_event.is_set():
        elapsed_time = time.time() - start_time
        logger.info(
            f"Transcripción en curso... ({elapsed_time:.0f} segundos transcurridos)"
        )
        stop_event.wait(interval_seconds)
    logger.info("Heartbeat de transcripción detenido.")


def process_transcription(
    youtube_url: str,
    title: str,
    language: str | None = None,
):
    """
    Lógica principal para descargar, transcribir y guardar la transcripción.
    Adaptada de la función transcribe_video_endpoint en main.py.
    """
    global _whisper_model_instance, _whisper_device_used

    logger.info(f"Petición de transcripción para URL: {youtube_url}, Título: {title}")

    if _whisper_model_instance is None:
        logger.error("Modelo Whisper no cargado. Intentando cargar ahora...")
        load_whisper_model_globally()  # Asegurarse de que el modelo esté cargado
        if (
            _whisper_model_instance is None
        ):  # Si aún no está cargado después del intento
            logger.critical("No se pudo cargar el modelo Whisper. Abortando.")
            return None  # O sys.exit(1)

    video_path_temp: str | None = None
    audio_path_temp: str | None = None
    downloaded_video_id: str | None = None

    unique_job_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    job_temp_dir = os.path.join(config.TEMP_DOWNLOAD_DIR, unique_job_id)
    utils.ensure_dir_exists(job_temp_dir)

    # Crear un evento para detener el hilo del heartbeat
    heartbeat_stop_event = threading.Event()
    # Crear e iniciar el hilo del heartbeat (cada 60 segundos)
    heartbeat_thread = threading.Thread(
        target=log_heartbeat,
        args=(60, heartbeat_stop_event),
        daemon=True,  # El hilo se cerrará automáticamente si el programa principal termina
    )
    heartbeat_thread.start()

    try:
        # Paso 1: Asegurar que los directorios de trabajo existen
        utils.ensure_dir_exists(config.TEMP_DOWNLOAD_DIR)
        utils.ensure_dir_exists(config.OUTPUT_TRANSCRIPTS_DIR)

        # Normalizar el título proporcionado por el usuario para el nombre de archivo final.
        user_provided_title = utils.normalize_title_for_filename(title)
        if not user_provided_title:
            logger.warning(
                f"Título original '{title}' normalizado a vacío. Usando 'untitled'."
            )
            user_provided_title = "untitled"

        # Paso 2: Descargar video y extraer audio
        logger.info(f"Descargando video desde: {youtube_url}")

        # Llamada directa a la función de downloader.py
        # download_and_extract_audio devuelve: (video_path, audio_path, video_id)
        vid_path, aud_path, vid_id = downloader.download_and_extract_audio(
            youtube_url=youtube_url,
            temp_dir=job_temp_dir,
            unique_job_id=unique_job_id,
        )

        video_path_temp = vid_path
        audio_path_temp = aud_path
        downloaded_video_id = vid_id

        if not audio_path_temp or not os.path.exists(audio_path_temp):
            # Esta comprobación es importante, ya que DownloadError podría no haberse lanzado
            # si yt-dlp tuvo éxito pero ffmpeg falló silenciosamente o el audio no se generó.
            logger.error(
                "El archivo de audio no fue creado o no se encontró después del proceso de descarga/extracción."
            )
            raise DownloadError(
                "El archivo de audio WAV no fue generado correctamente por ffmpeg/post-yt-dlp."
            )
        logger.info(f"Archivo de audio extraído en: {audio_path_temp}")
        if video_path_temp and os.path.exists(video_path_temp):
            logger.info(f"Archivo de video temporal en: {video_path_temp}")

        # Paso 3: Transcribir el audio
        logger.info(f"Transcribiendo archivo de audio: {audio_path_temp}")

        # Llamada directa a la función de transcriber.py
        trans_result: TranscriptionResult | None = transcriber.transcribe_audio_file(
            audio_path=audio_path_temp,
            model=_whisper_model_instance,  # Usar el modelo globalmente cargado
            language=language,  # Pasar el código de idioma
        )

        if not trans_result or not trans_result.text:
            logger.error("La transcripción no devolvió texto.")
            raise TranscriptionError("La transcripción resultó en texto vacío o nulo.")

        logger.info(
            f"Transcripción completada. Idioma detectado: {trans_result.language}. Longitud: {len(trans_result.text)} caracteres."
        )

        # Detener el hilo del heartbeat antes de finalizar
        heartbeat_stop_event.set()
        # Opcional: esperar a que el hilo termine (bueno para asegurar logs)
        # heartbeat_thread.join()

        # Paso 4: Guardar la transcripción en un archivo
        output_filename_base = (
            f"{user_provided_title}_vid_{downloaded_video_id}_job_{unique_job_id}"
        )

        logger.info(f"Guardando transcripción como: {output_filename_base}.txt")
        output_file_path = utils.save_transcription_to_file(
            transcription_text=trans_result.text,
            output_filename_no_ext=output_filename_base,
            output_dir=config.OUTPUT_TRANSCRIPTS_DIR,
            original_title=title,
        )

        if output_file_path is None:
            logger.critical(
                f"CRÍTICO: Fallo al guardar el archivo de transcripción para '{output_filename_base}' en '{config.OUTPUT_TRANSCRIPTS_DIR}'"
            )
            raise IOError("No se pudo guardar el archivo de transcripción.")

        logger.info(f"Transcripción guardada exitosamente en: {output_file_path}")
        print(
            f"Transcripción guardada en: {output_file_path}"
        )  # Salida para el usuario
        return output_file_path

    except DownloadError as e:
        error_message = str(e)
        logger.error(f"Error de descarga: {error_message}", exc_info=True)
        print(f"Error: No se pudo descargar el video. {error_message}", file=sys.stderr)
        # Asegurarse de detener el heartbeat en caso de error
        heartbeat_stop_event.set()
        # heartbeat_thread.join()
        return None
    except TranscriptionError as e:
        error_message = str(e)
        logger.error(f"Error de transcripción: {error_message}", exc_info=True)
        print(
            f"Error: No se pudo transcribir el audio. {error_message}", file=sys.stderr
        )
        # Asegurarse de detener el heartbeat en caso de error
        heartbeat_stop_event.set()
        # heartbeat_thread.join()
        return None
    except IOError as e:  # Específicamente para el fallo de guardado
        logger.critical(f"Error de E/S (ej. al guardar archivo): {e}", exc_info=True)
        print(f"Error: No se pudo guardar el archivo. {e}", file=sys.stderr)
        # Asegurarse de detener el heartbeat en caso de error
        heartbeat_stop_event.set()
        # heartbeat_thread.join()
        return None
    except Exception as e:
        logger.critical(
            f"Ocurrió un error inesperado durante el proceso: {e}", exc_info=True
        )
        print(f"Error inesperado: {e}", file=sys.stderr)
        # Asegurarse de detener el heartbeat en caso de error
        heartbeat_stop_event.set()
        # heartbeat_thread.join()
        return None
    finally:
        # Limpieza de la subcarpeta temporal del job
        utils.cleanup_temp_dir(job_temp_dir)


def get_youtube_title(youtube_url: str) -> str:
    """
    Extrae el título de un video de YouTube usando yt-dlp sin descargar el video.
    """
    try:
        import yt_dlp

        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if isinstance(info, dict):
                return info.get("title", "untitled")
            else:
                return "untitled"
    except Exception as e:
        logger.error(f"No se pudo extraer el título automáticamente: {e}")
        return "untitled"


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe un video de YouTube a texto. Solo requiere la URL."
    )
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        type=str,
        help="URL completa del video de YouTube (ej. https://www.youtube.com/watch?v=XXXXXXXXXXX)",
    )
    args = parser.parse_args()

    # Validar la URL de YouTube (simple check, yt-dlp hará la validación exhaustiva)
    if not (
        args.url.startswith("https://www.youtube.com/")
        or args.url.startswith("https://youtu.be/")
    ):
        print(
            "Error: La URL proporcionada no parece ser una URL válida de YouTube.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Extraer el título automáticamente
    logger.info("Extrayendo título automáticamente de YouTube...")
    title = get_youtube_title(args.url)
    logger.info(f"Título extraído: {title}")

    # Cargar el modelo Whisper antes de procesar, para que esté disponible
    load_whisper_model_globally()

    result_path = process_transcription(
        youtube_url=args.url,
        title=title,
        language=None,  # No se pasa idioma, Whisper lo detecta automáticamente
    )

    if result_path:
        logger.info("Proceso completado exitosamente.")
        sys.exit(0)
    else:
        logger.error("El proceso de transcripción falló.")
        sys.exit(1)


if __name__ == "__main__":
    main()
