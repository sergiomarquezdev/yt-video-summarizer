# Módulo para descargar videos de YouTube y extraer audio
import logging
from dataclasses import dataclass
from pathlib import Path

import yt_dlp

from yt_transcriber import utils


logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Excepción personalizada para errores de descarga."""

    pass


@dataclass
class DownloadResult:
    """Contiene los resultados de una descarga exitosa."""

    audio_path: Path
    video_path: Path | None
    video_id: str


def download_and_extract_audio(
    youtube_url: str,
    temp_dir: Path,
    unique_job_id: str,
    ffmpeg_location: str | None = None,
) -> DownloadResult:
    """
    Descarga un video de YouTube, extrae su audio y lo guarda en formato WAV.

    Args:
        youtube_url: La URL del video de YouTube.
        temp_dir: El directorio donde se guardarán los archivos temporales.
        unique_job_id: Un identificador único para esta tarea.

    Returns:
        Un objeto DownloadResult con las rutas de los archivos y el ID del video.

    Raises:
        DownloadError: Si ocurre un error durante la descarga o extracción.
    """
    logger.info(f"Iniciando descarga para URL: {youtube_url}, job_id: {unique_job_id}")
    utils.ensure_dir_exists(temp_dir)

    try:
        # 1. Extraer información del video, incluido su ID
        info_opts = {"quiet": True, "noplaylist": True, "logger": logger}
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            video_id = info_dict.get("id")
            if not video_id:
                raise DownloadError(f"No se pudo extraer el ID del video de la URL: {youtube_url}")
        logger.info(f"Video ID extraído: {video_id}")

        # 2. Configurar la descarga con nombres de archivo predecibles
        base_filename = f"{video_id}_{unique_job_id}"
        output_template = temp_dir / f"{base_filename}.%(ext)s"
        expected_audio_path = temp_dir / f"{base_filename}.wav"

        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": False,
            "noplaylist": True,
            "keepvideo": True,
            "outtmpl": str(output_template),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "nopostoverwrites": False,
                }
            ],
            "postprocessor_args": {"FFmpegExtractAudio": ["-ar", "16000", "-ac", "1"]},
            "logger": logger,
        }

        # Agregar ruta de FFmpeg si se proporciona
        if ffmpeg_location:
            ydl_opts["ffmpeg_location"] = ffmpeg_location
            logger.info(f"Usando FFmpeg desde: {ffmpeg_location}")

        # 3. Ejecutar la descarga y el post-procesamiento
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            download_info = ydl.extract_info(youtube_url, download=True)
            video_path_str = ydl.prepare_filename(download_info)
            video_path = (
                Path(video_path_str) if video_path_str and Path(video_path_str).exists() else None
            )

        # 4. Verificar el resultado
        if not expected_audio_path.exists():
            logger.error(
                f"Fallo crítico: Audio WAV no encontrado en la ruta esperada: '{expected_audio_path}'"
            )
            if video_path:
                try:
                    video_path.unlink()
                except OSError as e_clean:
                    logger.error(
                        f"Error limpiando video '{video_path}' tras fallo de audio: {e_clean}"
                    )
            raise DownloadError(f"La extracción de audio falló para el video ID {video_id}.")

        logger.info(f"Audio extraído correctamente a: {expected_audio_path}")
        if video_path:
            logger.info(f"Video descargado a: {video_path}")

        return DownloadResult(
            audio_path=expected_audio_path,
            video_path=video_path,
            video_id=video_id,
        )

    except yt_dlp.utils.DownloadError as e_yt:
        logger.error(f"Error de yt-dlp para '{youtube_url}': {e_yt}")
        raise DownloadError(f"yt-dlp falló: {e_yt}") from e_yt
    except Exception as e_gen:
        logger.error(f"Error inesperado en descarga para '{youtube_url}': {e_gen}", exc_info=True)
        raise DownloadError(f"Error general en descarga: {e_gen}") from e_gen
