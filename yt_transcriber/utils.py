import logging
import os
import re

logger = logging.getLogger(__name__)


def normalize_title_for_filename(text: str) -> str:
    """
    Normaliza un texto para ser usado como parte de un nombre de archivo.
    - Conserva alfanuméricos, espacios y guiones.
    - Elimina otros caracteres.
    - Reemplaza espacios/guiones múltiples con un solo guion bajo.
    - Elimina guiones bajos al inicio/final.
    """
    if not text:
        return "untitled"
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    text = text.strip("_")
    if not text:
        return "untitled"
    return text


def ensure_dir_exists(dir_path: str):
    """
    Asegura que un directorio exista. Si no, lo crea.

    Args:
        dir_path: Ruta del directorio a verificar/crear.
    """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            logger.info(f"Directorio creado: {dir_path}")
        except OSError as e:
            logger.error(f"Error al crear el directorio {dir_path}: {e}")
            raise
    else:
        logger.debug(f"Directorio ya existe: {dir_path}")


def save_transcription_to_file(
    transcription_text: str,
    output_filename_no_ext: str,
    output_dir: str,
    original_title: str | None = None,
) -> str | None:
    """
    Guarda el texto de la transcripción en un archivo .txt.

    Args:
        transcription_text: El texto a guardar.
        output_filename_no_ext: Nombre del archivo de salida (sin extensión).
        output_dir: Directorio donde se guardará el archivo.
        original_title: Título original del video, para incluirlo como comentario.

    Returns:
        La ruta completa al archivo guardado, o None si ocurre un error.
    """
    try:
        ensure_dir_exists(output_dir)

        safe_filename = "".join(
            c if c.isalnum() or c in (".", "_") else "_" for c in output_filename_no_ext
        ).strip(" .")

        if not safe_filename:
            safe_filename = f"default_transcription_{output_filename_no_ext[:10]}"

        file_path = os.path.join(output_dir, f"{safe_filename}.txt")

        content_to_write = transcription_text
        if original_title:
            content_to_write = (
                f"# Original Video Title: {original_title}\n\n{transcription_text}"
            )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_to_write)
        logger.info(f"Transcripción guardada en: {file_path}")
        return file_path
    except Exception as e:
        logger.error(
            f"Error al guardar la transcripción para '{output_filename_no_ext}' en '{output_dir}': {e}",
            exc_info=True,
        )
        return None


def cleanup_temp_files(file_paths_to_delete: list[str | None]):
    """
    Elimina una lista de archivos temporalmente.

    Args:
        file_paths_to_delete: Una lista de rutas de archivos a eliminar.
                              Puede contener Nones, que serán ignorados.
    """
    cleaned_count = 0
    valid_paths_to_check = [p for p in file_paths_to_delete if p]

    for file_path in valid_paths_to_check:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Archivo temporal eliminado: {file_path}")
                cleaned_count += 1
            except OSError as e:
                logger.error(f"Error al eliminar el archivo temporal {file_path}: {e}")
        else:
            logger.warning(
                f"Se intentó limpiar el archivo temporal {file_path}, pero no existe."
            )
    logger.info(
        f"Limpieza de archivos temporales: {cleaned_count} archivo(s) eliminado(s) de {len(valid_paths_to_check)} solicitado(s) (existentes)."
    )


def cleanup_temp_files_sync(file_paths_to_delete: list[str | None]):
    """
    Elimina una lista de archivos de forma síncrona.
    Usado para limpieza inmediata en caso de errores.
    """
    valid_paths_to_check = [p for p in file_paths_to_delete if p]
    if not valid_paths_to_check:
        logger.info("Limpieza síncrona: No hay archivos válidos para eliminar.")
        return

    logger.info(f"Limpieza síncrona iniciada para: {valid_paths_to_check}")
    deleted_count = 0
    for file_path in valid_paths_to_check:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
                logger.info(f"Archivo temporal (sync) eliminado: {file_path}")
            else:
                logger.warning(
                    f"Archivo temporal (sync) no encontrado para eliminar: {file_path}"
                )
        except OSError as e_clean:
            logger.error(
                f"Error eliminando archivo temporal (sync) {file_path}: {e_clean}"
            )
        except Exception as e_unexpected:
            logger.error(
                f"Error inesperado eliminando archivo (sync) {file_path}: {e_unexpected}",
                exc_info=True,
            )
    logger.info(
        f"Limpieza síncrona completada: {deleted_count} archivo(s) eliminado(s) de {len(valid_paths_to_check)} solicitado(s) (existentes)."
    )
