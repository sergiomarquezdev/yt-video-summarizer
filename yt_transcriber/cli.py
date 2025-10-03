import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from yt_transcriber import config, downloader, transcriber, utils
from yt_transcriber.downloader import DownloadError
from yt_transcriber.transcriber import TranscriptionError


# Configuración del logger
logger = logging.getLogger(__name__)


def setup_logging():
    """Configura el logging básico para la aplicación."""
    logging.basicConfig(
        level=config.settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def load_whisper_model():
    """Carga y devuelve el modelo Whisper según la configuración."""
    logger.info("Cargando modelo Whisper...")
    try:
        import torch
        import whisper
    except ImportError as e:
        logger.critical(
            f"Dependencias críticas no encontradas. Asegúrate de que torch y whisper estén instalados. Error: {e}"
        )
        sys.exit(1)

    device = config.settings.WHISPER_DEVICE
    if device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA no disponible. Cambiando a CPU para Whisper.")
        device = "cpu"

    try:
        model = whisper.load_model(config.settings.WHISPER_MODEL_NAME, device=device)
        logger.info(f"Modelo Whisper '{config.settings.WHISPER_MODEL_NAME}' cargado en '{device}'.")
        return model
    except Exception as e:
        logger.critical(
            f"Fallo CRÍTICO al cargar modelo Whisper en '{device}'. Error: {e}",
            exc_info=True,
        )
        sys.exit(1)


def get_youtube_title(youtube_url: str) -> str:
    """Extrae el título de un video de YouTube usando yt-dlp."""
    try:
        import yt_dlp

        with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if info is None:
                return "untitled"
            title: str = info.get("title", "untitled")  # type: ignore[assignment]
            return title
    except Exception as e:
        logger.error(f"No se pudo extraer el título automáticamente: {e}")
        return "untitled"


def process_transcription(
    youtube_url: str,
    title: str,
    model,
    language: str | None = None,
    ffmpeg_location: str | None = None,
) -> Path | None:
    """
    Lógica principal para descargar, transcribir y guardar la transcripción.
    """
    logger.info(f"Iniciando transcripción para URL: {youtube_url}")
    unique_job_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    job_temp_dir = config.settings.TEMP_DOWNLOAD_DIR / unique_job_id

    try:
        # 1. Descargar video y extraer audio
        logger.info("Paso 1: Descargando y extrayendo audio...")
        download_result = downloader.download_and_extract_audio(
            youtube_url=youtube_url,
            temp_dir=job_temp_dir,
            unique_job_id=unique_job_id,
            ffmpeg_location=ffmpeg_location,
        )
        logger.info(f"Audio extraído a: {download_result.audio_path}")

        # 2. Transcribir el audio
        logger.info("Paso 2: Transcribiendo audio...")
        transcription_result = transcriber.transcribe_audio_file(
            audio_path=download_result.audio_path, model=model, language=language
        )
        logger.info(f"Transcripción completada. Idioma detectado: {transcription_result.language}")

        # 3. Guardar la transcripción
        logger.info("Paso 3: Guardando transcripción...")
        normalized_title = utils.normalize_title_for_filename(title)
        output_filename_base = (
            f"{normalized_title}_vid_{download_result.video_id}_job_{unique_job_id}"
        )
        output_file_path = utils.save_transcription_to_file(
            transcription_text=transcription_result.text,
            output_filename_no_ext=output_filename_base,
            output_dir=config.settings.OUTPUT_TRANSCRIPTS_DIR,
            original_title=title,
        )

        if not output_file_path:
            raise OSError("No se pudo guardar el archivo de transcripción.")

        logger.info(f"Transcripción guardada exitosamente en: {output_file_path}")
        print(f"\nTranscripción guardada en: {output_file_path}")
        return output_file_path

    except (OSError, DownloadError, TranscriptionError) as e:
        logger.error(f"Ha ocurrido un error en el proceso: {e}", exc_info=True)
        print(f"\nError: {e}", file=sys.stderr)
        return None
    except Exception as e:
        logger.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
        print(f"\nError inesperado: {e}", file=sys.stderr)
        return None
    finally:
        # 4. Limpieza
        logger.info(f"Limpiando directorio temporal: {job_temp_dir}")
        utils.cleanup_temp_dir(job_temp_dir)


def main():
    """Punto de entrada principal para el CLI."""
    parser = argparse.ArgumentParser(description="Transcribe un video de YouTube a texto.")
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        type=str,
        help="URL completa del video de YouTube.",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default=None,
        help="Código de idioma (ej. 'en', 'es') para forzar la transcripción en ese idioma.",
    )
    parser.add_argument(
        "--ffmpeg-location",
        type=str,
        default=None,
        help="Ruta personalizada a FFmpeg (ej. 'C:\\ffmpeg\\bin\\ffmpeg.exe').",
    )
    args = parser.parse_args()

    setup_logging()

    # Validar la URL de YouTube
    if not (
        args.url.startswith("https://www.youtube.com/") or args.url.startswith("https://youtu.be/")
    ):
        logger.error(f"URL de YouTube no válida: {args.url}")
        print("Error: La URL no parece ser una URL válida de YouTube.", file=sys.stderr)
        sys.exit(1)

    # Cargar el modelo Whisper
    model = load_whisper_model()

    # Obtener título y procesar
    logger.info("Extrayendo título del video...")
    title = get_youtube_title(args.url)
    logger.info(f"Título extraído: {title}")

    result_path = process_transcription(
        youtube_url=args.url,
        title=title,
        model=model,
        language=args.language,
        ffmpeg_location=args.ffmpeg_location,
    )

    if result_path:
        logger.info("Proceso completado exitosamente.")
        sys.exit(0)
    else:
        logger.error("El proceso de transcripción falló.")
        sys.exit(1)


if __name__ == "__main__":
    main()
