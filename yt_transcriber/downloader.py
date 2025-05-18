# Módulo para descargar videos de YouTube y extraer audio

import logging
import os

import yt_dlp

logger = logging.getLogger(__name__)
# La configuración de logging basicConfig se maneja en main.py


# Excepción personalizada para errores de descarga
class DownloadError(Exception):
    pass


def download_and_extract_audio(
    youtube_url: str, temp_dir: str, unique_job_id: str
) -> tuple[str | None, str, str | None]:  # Devuelve (video_path, audio_path, video_id)
    """
    Descarga un video de YouTube, extrae su audio y lo guarda en formato WAV.
    Los nombres de archivo se basan en el ID del video y un ID de trabajo único.

    Args:
        youtube_url: La URL del video de YouTube.
        temp_dir: El directorio donde se guardarán los archivos temporales.
        unique_job_id: Un identificador único para esta tarea de descarga/transcripción.

    Returns:
        Una tupla (ruta_video_temporal, ruta_audio_wav, video_id).
        ruta_video_temporal puede ser None si el video no se guarda o no se encuentra.
        video_id puede ser None si no se puede extraer.

    Raises:
        DownloadError: Si ocurre un error durante la descarga o extracción de audio.
    """
    logger.info(f"Iniciando descarga para URL: {youtube_url}, job_id: {unique_job_id}")

    # Asegurar que el directorio temporal del job existe
    from yt_transcriber import utils

    utils.ensure_dir_exists(temp_dir)

    video_id: str | None = None

    ydl_opts_template = {
        "format": "bestaudio/best",
        # "format": "bestvideo[ext=mp4][height<=1080]+bestaudio/best[ext=mp4][height<=1080]/best",
        "quiet": False,
        "noplaylist": True,
        "keepvideo": True,  # Necesario para tener la ruta del video si se retiene
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "nopostoverwrites": False,
            }
        ],
        "postprocessor_args": {"FFmpegExtractAudio": ["-ar", "16000", "-ac", "1"]},
        "logger": logger,
        "progress_hooks": [
            lambda d: logger.debug(
                f"yt-dlp hook: {d['status']}, info: {d.get('filename')}"
            )
            if d["status"] in ["downloading", "finished"]
            else None
        ],
    }

    downloaded_video_path: str | None = None
    expected_audio_wav_path: str

    try:
        # Primero, obtener el video_id para usarlo en los nombres de archivo.
        logger.debug(f"Extrayendo info para video ID de: {youtube_url}")
        with yt_dlp.YoutubeDL(
            {"quiet": True, "noplaylist": True, "logger": logger}
        ) as ydl_info:
            info_dict_pre = ydl_info.extract_info(youtube_url, download=False)
            video_id = (
                info_dict_pre.get("id") if isinstance(info_dict_pre, dict) else None
            )

        if not video_id:
            logger.warning(
                f"No se pudo extraer video_id para {youtube_url}. Usando fallback."
            )
            video_id = f"unknownID_{unique_job_id[:8]}"  # Fallback ID más corto
        else:
            logger.info(f"Video ID extraído: {video_id} para {youtube_url}")

        base_filename_no_ext = f"{video_id}_{unique_job_id}"
        video_output_template = os.path.join(
            temp_dir, f"{base_filename_no_ext}.%(ext)s"
        )
        expected_audio_wav_path = os.path.join(temp_dir, f"{base_filename_no_ext}.wav")

        ydl_opts = ydl_opts_template.copy()
        ydl_opts["outtmpl"] = video_output_template

        logger.debug(f"Opciones finales de yt-dlp para descarga: {ydl_opts}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict_download = ydl.extract_info(youtube_url, download=True)
            # El nombre de archivo descargado puede incluir información de la extensión real.
            downloaded_video_path = ydl.prepare_filename(info_dict_download)

            if not downloaded_video_path or not os.path.exists(downloaded_video_path):
                logger.warning(
                    f"Ruta de video no determinada o archivo no existe: '{downloaded_video_path}' (ID: '{video_id}')."
                )
                downloaded_video_path = None
            else:
                logger.info(f"Video descargado a: {downloaded_video_path}")

            # El audio debe existir en expected_audio_wav_path por la config del postprocesador.
            if os.path.exists(expected_audio_wav_path):
                logger.info(
                    f"Audio extraído correctamente a: {expected_audio_wav_path}"
                )
                return (
                    downloaded_video_path,
                    expected_audio_wav_path,
                    video_id,
                )  # video_path puede ser None
            else:
                # Fallback por si el nombre del WAV no es exactamente el esperado.
                possible_audio_files = [
                    f
                    for f in os.listdir(temp_dir)
                    if f.startswith(base_filename_no_ext) and f.endswith(".wav")
                ]
                if possible_audio_files:
                    actual_audio_path = os.path.join(temp_dir, possible_audio_files[0])
                    logger.warning(
                        f"Audio WAV no en '{expected_audio_wav_path}', pero encontrado en '{actual_audio_path}'."
                    )
                    return downloaded_video_path, actual_audio_path, video_id
                else:
                    logger.error(
                        f"Fallo crítico: Audio WAV no encontrado. Esperado: '{expected_audio_wav_path}' (base: {base_filename_no_ext})."
                    )
                    if downloaded_video_path and os.path.exists(downloaded_video_path):
                        try:
                            os.remove(downloaded_video_path)
                        except OSError as e_clean:
                            logger.error(
                                f"Error limpiando video '{downloaded_video_path}' tras fallo de audio: {e_clean}"
                            )
                    raise DownloadError(
                        f"Extracción de audio falló para {base_filename_no_ext}.wav"
                    )

    except yt_dlp.utils.DownloadError as e_yt:
        logger.error(f"Error de yt-dlp para '{youtube_url}': {e_yt}")
        raise DownloadError(f"yt-dlp falló: {e_yt}") from e_yt
    except Exception as e_gen:
        logger.error(
            f"Error inesperado en descarga para '{youtube_url}': {e_gen}", exc_info=True
        )
        raise DownloadError(f"Error general en descarga: {e_gen}") from e_gen
