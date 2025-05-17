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
    # Paso 1: Conservar solo alfanuméricos, espacios, y guiones.
    # Eliminar caracteres que no sean palabras (alfanuméricos y _), espacios, o guiones.
    text = re.sub(r"[^\w\s-]", "", text)
    # Paso 2: Reemplazar secuencias de espacios y/o guiones con un solo guion bajo.
    text = re.sub(r"[\s-]+", "_", text)
    # Paso 3: Eliminar guiones bajos al principio o final del nombre (si los hay).
    text = text.strip("_")
    # Si después de todo el texto queda vacío (ej. title era "---"), devolver un default.
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
            raise  # Relanzar la excepción para que el llamador la maneje si es crítico
    else:
        logger.debug(f"Directorio ya existe: {dir_path}")


def save_transcription_to_file(
    transcription_text: str, output_filename_no_ext: str, output_dir: str
) -> str | None:
    """
    Guarda el texto de la transcripción en un archivo .txt.

    Args:
        transcription_text: El texto a guardar.
        output_filename_no_ext: Nombre del archivo de salida (sin extensión).
        output_dir: Directorio donde se guardará el archivo.

    Returns:
        La ruta completa al archivo guardado, o None si ocurre un error.
    """
    try:
        ensure_dir_exists(output_dir)  # Asegurar que el directorio de salida exista

        # Sanitizar el nombre del archivo como medida de seguridad adicional.
        safe_filename = "".join(
            c
            if c.isalnum() or c in (".", "_")
            else "_"  # Permitir puntos y guiones bajos
            for c in output_filename_no_ext
        ).strip(" .")  # Eliminar espacios y puntos al inicio/final también

        if not safe_filename:  # Si la sanitización extrema lo deja vacío
            safe_filename = f"default_transcription_{output_filename_no_ext[:10]}"  # Fallback más único

        file_path = os.path.join(output_dir, f"{safe_filename}.txt")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(transcription_text)
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
    valid_paths_to_check = [
        p for p in file_paths_to_delete if p
    ]  # Filtrar Nones primero

    for file_path in valid_paths_to_check:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Archivo temporal eliminado: {file_path}")
                cleaned_count += 1
            except OSError as e:
                logger.error(f"Error al eliminar el archivo temporal {file_path}: {e}")
        else:  # file_path no es None aquí debido al filtro previo
            logger.warning(
                f"Se intentó limpiar el archivo temporal {file_path}, pero no existe."
            )
    logger.info(
        f"Limpieza de archivos temporales: {cleaned_count} archivo(s) eliminado(s) de {len(valid_paths_to_check)} solicitado(s) (existentes)."
    )


def cleanup_temp_files_sync(
    file_paths_to_delete: list[str | None],
):  # Permitir None también aquí
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
        # file_path ya está garantizado que no es None aquí
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
        except Exception as e_unexpected:  # Captura más general por si acaso
            logger.error(
                f"Error inesperado eliminando archivo (sync) {file_path}: {e_unexpected}",
                exc_info=True,
            )
    logger.info(
        f"Limpieza síncrona completada: {deleted_count} archivo(s) eliminado(s) de {len(valid_paths_to_check)} solicitado(s) (existentes)."
    )


if __name__ == "__main__":
    # Pruebas para las utilidades
    test_output_dir = "../output_transcripts/"
    test_temp_dir_utils = "../temp_files/"

    logger.info("--- Iniciando pruebas de utils.py ---")

    # Prueba ensure_dir_exists
    logger.info(f"Probando ensure_dir_exists para: {test_output_dir}")
    ensure_dir_exists(test_output_dir)
    logger.info(f"Probando ensure_dir_exists para: {test_temp_dir_utils}")
    ensure_dir_exists(test_temp_dir_utils)
    ensure_dir_exists(
        test_output_dir
    )  # Probar de nuevo para asegurar que no falla si ya existe

    # Prueba save_transcription_to_file
    test_text = "Esta es una prueba de transcripción.\nCon múltiples líneas."
    test_filename_valid = "mi_prueba_de_transcripción_normalizada"
    test_filename_problematic = "   !!!problemático???   ...nombre "

    logger.info(
        f"Probando save_transcription_to_file con nombre normalizado: {test_filename_valid}"
    )
    saved_path_1 = save_transcription_to_file(
        test_text, test_filename_valid, test_output_dir
    )
    if saved_path_1 and os.path.exists(saved_path_1):
        logger.info(f"Archivo de prueba (1) guardado en: {saved_path_1}")
    else:
        logger.error("Falló la prueba de save_transcription_to_file (1).")

    normalized_problematic = normalize_title_for_filename(test_filename_problematic)
    logger.info(
        f"Probando save_transcription_to_file con nombre problemático (normalizado a '{normalized_problematic}'): {test_filename_problematic}"
    )
    # La función save_transcription_to_file hará su propia sanitización interna a partir de output_filename_no_ext
    saved_path_2 = save_transcription_to_file(
        test_text, normalized_problematic, test_output_dir
    )
    if saved_path_2 and os.path.exists(saved_path_2):
        logger.info(f"Archivo de prueba (2) guardado en: {saved_path_2}")
    else:
        logger.error("Falló la prueba de save_transcription_to_file (2).")

    # Prueba cleanup_temp_files y cleanup_temp_files_sync
    dummy_files_info = {
        "dummy1.tmp": os.path.join(test_temp_dir_utils, "dummy_to_delete_1.tmp"),
        "dummy2.tmp": os.path.join(test_temp_dir_utils, "dummy_to_delete_2.tmp"),
        "dummy_sync1.tmp": os.path.join(test_temp_dir_utils, "dummy_sync_1.tmp"),
        "dummy_sync2.tmp": os.path.join(test_temp_dir_utils, "dummy_sync_2.tmp"),
    }
    non_existent_file = os.path.join(test_temp_dir_utils, "no_existe.tmp")

    for desc, path in dummy_files_info.items():
        with open(path, "w") as f:
            f.write(desc)

    files_for_async_clean = [
        dummy_files_info["dummy1.tmp"],
        dummy_files_info["dummy2.tmp"],
        non_existent_file,
        None,
    ]
    logger.info(f"Probando cleanup_temp_files (async) con: {files_for_async_clean}")
    cleanup_temp_files(files_for_async_clean)

    if os.path.exists(dummy_files_info["dummy1.tmp"]) or os.path.exists(
        dummy_files_info["dummy2.tmp"]
    ):
        logger.error("Falló cleanup_temp_files, archivos dummy aún existen.")
    else:
        logger.info("cleanup_temp_files parece exitosa (archivos dummy eliminados).")

    files_for_sync_clean = [
        dummy_files_info["dummy_sync1.tmp"],
        dummy_files_info["dummy_sync2.tmp"],
        non_existent_file,
        None,
    ]
    logger.info(f"Probando cleanup_temp_files_sync con: {files_for_sync_clean}")
    cleanup_temp_files_sync(files_for_sync_clean)

    if os.path.exists(dummy_files_info["dummy_sync1.tmp"]) or os.path.exists(
        dummy_files_info["dummy_sync2.tmp"]
    ):
        logger.error("Falló cleanup_temp_files_sync, archivos dummy_sync aún existen.")
    else:
        logger.info(
            "cleanup_temp_files_sync parece exitosa (archivos dummy_sync eliminados)."
        )

    logger.info("--- Fin de pruebas de utils.py ---")
