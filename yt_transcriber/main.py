# Punto de entrada principal de la aplicación FastAPI

import logging
import os
from datetime import datetime
from typing import Optional

import torch  # Necesario para la comprobación de CUDA y carga del modelo
import whisper  # Necesario para cargar el modelo y type hints
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi import Request as FastAPIRequest
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import (
    BaseModel,  # BaseModel para modelos de datos
    HttpUrl,  # HttpUrl para validación de URL
)

from yt_transcriber import config, downloader, transcriber, utils
from yt_transcriber.downloader import DownloadError
from yt_transcriber.transcriber import (
    TranscriptionError,
    TranscriptionResult,
)

logger = logging.getLogger(__name__)

# Determinar el nivel de log numérico desde la configuración
# getattr se usa para obtener el atributo del módulo logging (ej. logging.INFO)
# Si config.LOG_LEVEL no es un nombre válido, default a logging.INFO
numeric_log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)

logging.basicConfig(
    level=numeric_log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        # Podrías añadir FileHandler aquí si quieres logs persistentes
    ],
)

app = FastAPI(
    title="YouTube Transcription Service",
    description="API para descargar videos de YouTube, transcribirlos y guardar el texto.",
    version="0.1.0",
)


# --- Modelos Pydantic para Respuestas de Error Estructuradas ---
class ApiErrorDetail(BaseModel):
    status_code: int
    error_type: str
    message: str
    detail: Optional[str] = None


# --- Manejadores de Excepciones Globales ---
@app.exception_handler(DownloadError)
async def download_error_exception_handler(request: FastAPIRequest, exc: DownloadError):
    logger.error(f"DownloadError capturada por handler: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ApiErrorDetail(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_type=type(exc).__name__,
            message="Error durante la descarga del video.",
            detail=str(exc),
        ).model_dump(),
    )


@app.exception_handler(TranscriptionError)
async def transcription_error_exception_handler(
    request: FastAPIRequest, exc: TranscriptionError
):
    logger.error(f"TranscriptionError capturada por handler: {exc}", exc_info=True)
    # Limpiar archivos si la transcripción falla.
    # Esta lógica es un poco difícil de manejar aquí sin acceso directo a video_path_temp, audio_path_temp
    # Considerar si la limpieza debe ser responsabilidad del endpoint o si se puede pasar info al error.
    # Por ahora, mantenemos la limpieza dentro del endpoint y este handler solo reporta.
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type=type(exc).__name__,
            message="Error durante la transcripción del audio.",
            detail=str(exc),
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: FastAPIRequest, exc: HTTPException):
    logger.info(
        f"HTTPException capturada (formateando con ApiErrorDetail): {exc.status_code} - {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiErrorDetail(
            status_code=exc.status_code,
            error_type=type(
                exc
            ).__name__,  # Usar el nombre de la clase de la excepción específica si es posible
            message="Ocurrió una excepción HTTP.",  # Mensaje genérico
            detail=exc.detail,  # Detalle específico de la excepción HTTP
        ).model_dump(),
        headers=exc.headers,  # Conservar las cabeceras originales de la HTTPException
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: FastAPIRequest, exc: Exception):
    logger.critical(
        f"Excepción genérica no controlada capturada por handler: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiErrorDetail(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type=type(exc).__name__,
            message="Ocurrió un error interno inesperado en el servidor.",
            detail="Por favor, contacte al administrador si el problema persiste.",  # No exponer str(exc) directamente por seguridad
        ).model_dump(),
    )


# --- Evento de Inicio de la Aplicación para Cargar el Modelo Whisper ---
@app.on_event("startup")
async def load_whisper_model_on_startup():
    logger.info("Evento de inicio: Cargando modelo Whisper...")
    device_to_use = config.WHISPER_DEVICE
    if device_to_use == "cuda" and not torch.cuda.is_available():
        logger.warning(
            "CUDA no disponible según torch.cuda.is_available(). Cambiando a CPU para Whisper."
        )
        device_to_use = "cpu"

    try:
        model = whisper.load_model(config.WHISPER_MODEL_NAME, device=device_to_use)
        app.state.whisper_model = model
        app.state.whisper_device_used = (
            device_to_use  # Guardar el dispositivo realmente usado
        )
        logger.info(
            f"Modelo Whisper '{config.WHISPER_MODEL_NAME}' cargado exitosamente en '{device_to_use}'."
        )
    except Exception as e:
        logger.critical(
            f"Fallo CRÍTICO al cargar modelo Whisper '{config.WHISPER_MODEL_NAME}' en '{device_to_use}'. Error: {e}",
            exc_info=True,
        )
        # Permitir que la aplicación falle si el modelo no se carga (componente crítico).
        # Alternativa: app.state.whisper_model = None y chequear en endpoints,
        # pero fallar rápido es a menudo preferible para dependencias críticas.
        raise RuntimeError(f"No se pudo cargar el modelo Whisper: {e}") from e


# --- Modelos Pydantic para validación de datos ---
class TranscriptionRequest(BaseModel):
    youtube_url: HttpUrl  # Validada por Pydantic como URL HTTP/HTTPS
    title: str
    language: Optional[str] = (
        None  # Opcional: código de idioma para Whisper (ej. "en", "es")
    )
    include_timestamps: bool = False  # Opcional: incluir timestamps en la salida (actualmente solo afecta opciones de decodificación)


class TranscriptionResponse(BaseModel):
    message: str
    filename: str
    original_url: HttpUrl
    transcription_length: int
    detected_language: str | None = None  # Idioma detectado por Whisper
    transcript_preview: str | None = (
        None  # Vista previa de la transcripción (primeros 200 chars)
    )


# --- Lógica del Endpoint ---
@app.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ApiErrorDetail,
            "description": "Entrada inválida (ej. JSON malformado)",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ApiErrorDetail,
            "description": "Error de validación Pydantic (ej. URL inválida, falta título)",
        },  # FastAPI usa su propio formato para 422 por defecto
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApiErrorDetail,
            "description": "Error interno del servidor",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApiErrorDetail,
            "description": "Error en descarga o procesamiento del video",
        },
    },
)
async def transcribe_video_endpoint(
    fastapi_request: FastAPIRequest,  # Objeto Request de FastAPI para acceder a app.state
    transcription_request: TranscriptionRequest,  # Datos de la petición validados por Pydantic
    background_tasks: BackgroundTasks,  # Para tareas en segundo plano (limpieza)
):
    """
    Endpoint para descargar un video de YouTube, transcribirlo y guardar el texto.

    Args:
        fastapi_request: La instancia de la petición de FastAPI.
        transcription_request: Los datos de la petición validados.
        background_tasks: Utilidad de FastAPI para tareas en segundo plano.
    """
    logger.info(
        f"Petición de transcripción para URL: {transcription_request.youtube_url}, Título: {transcription_request.title}"
    )

    # Verificar si el modelo Whisper está cargado (desde app.state)
    if (
        not hasattr(fastapi_request.app.state, "whisper_model")
        or fastapi_request.app.state.whisper_model is None
    ):
        logger.error("Modelo Whisper no cargado. No se puede procesar la petición.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error interno: Modelo de transcripción no disponible.",
        )

    video_path_temp: str | None = None
    audio_path_temp: str | None = None
    downloaded_video_id: str | None = None  # ID del video extraído por el downloader

    unique_job_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

    try:
        # Paso 1: Asegurar que los directorios de trabajo existen
        utils.ensure_dir_exists(config.TEMP_DOWNLOAD_DIR)
        utils.ensure_dir_exists(config.OUTPUT_TRANSCRIPTS_DIR)

        # Normalizar el título proporcionado por el usuario para el nombre de archivo final.
        user_provided_title = utils.normalize_title_for_filename(
            transcription_request.title
        )
        if not user_provided_title:  # Si la normalización resulta en un string vacío
            logger.warning(
                f"Título original '{transcription_request.title}' normalizado a vacío. Usando 'untitled'."
            )
            user_provided_title = "untitled"

        logger.info(
            f"Procesando: URL={transcription_request.youtube_url}, TítuloBase={user_provided_title}, JobID={unique_job_id}"
        )

        # downloader.download_and_extract_audio devuelve (video_path|None, audio_path, video_id|None)
        (
            temp_video_path_or_empty,
            audio_path_temp,
            downloaded_video_id,
        ) = await run_in_threadpool(
            downloader.download_and_extract_audio,
            str(transcription_request.youtube_url),
            config.TEMP_DOWNLOAD_DIR,
            unique_job_id,  # Se pasa el job_id para nombres de archivo únicos en downloader
        )
        video_path_temp = temp_video_path_or_empty if temp_video_path_or_empty else None

        if not downloaded_video_id:
            downloaded_video_id = (
                "unknownVideoID"  # Fallback si downloader no pudo obtenerlo
            )
            logger.warning(
                f"Downloader no retornó video_id; usando {downloaded_video_id}."
            )

        logger.info(
            f"Descarga OK. Audio: {audio_path_temp}, Video: {video_path_temp}, VideoID: {downloaded_video_id}"
        )

        # La condición crítica es la existencia del archivo de audio.
        # video_path_temp (si es None) se maneja en la limpieza; su ausencia no debe
        # detener la transcripción si el audio está presente.
        if not audio_path_temp:
            logger.error("Fallo crítico: No se obtuvo ruta al archivo de audio.")
            if video_path_temp and os.path.exists(video_path_temp):
                logger.info(
                    f"Programando limpieza de video {video_path_temp} por fallo de audio."
                )
                background_tasks.add_task(utils.cleanup_temp_files, [video_path_temp])
            raise DownloadError("No se pudo obtener el archivo de audio procesado.")

        logger.info(
            f"Audio para transcribir: {audio_path_temp}, Video temp: {video_path_temp}"
        )

        # 3. Transcribir el archivo de audio
        logger.info(f"Llamando a transcriber para: {audio_path_temp}")
        # Usar el modelo del app.state
        whisper_model_instance = fastapi_request.app.state.whisper_model
        transcription_result: TranscriptionResult = await run_in_threadpool(
            transcriber.transcribe_audio_file,
            audio_path_temp,
            whisper_model_instance,  # Pasar la instancia del modelo cargado
            transcription_request.language,  # Pasar el idioma solicitado
            transcription_request.include_timestamps,  # Pasar la opción de timestamps
        )

        if (
            transcription_result is None or transcription_result.text is None
        ):  # Chequeo más robusto
            # Si transcribe_audio_file fue modificado para devolver None en error,
            # o si TranscriptionResult.text puede ser None.
            logger.error(
                "Fallo en la transcripción del audio o texto vacío. No se puede continuar."
            )
            raise TranscriptionError(
                "La transcripción del audio falló o no produjo texto."
            )

        logger.info(
            f"Audio transcrito exitosamente. Longitud: {len(transcription_result.text)} caracteres. Idioma: {transcription_result.language}"
        )

        # 4. Guardar la transcripción en un archivo .txt
        logger.info(
            f"Guardando transcripción con título normalizado: {user_provided_title}"
        )
        # Construir nombre de archivo de salida final
        if user_provided_title in ["untitled", "default_title"]:
            output_filename_base = (
                f"transcription_vid_{downloaded_video_id}_job_{unique_job_id}"
            )
        else:
            output_filename_base = (
                f"{user_provided_title}_vid_{downloaded_video_id}_job_{unique_job_id}"
            )

        output_file_path = await run_in_threadpool(
            utils.save_transcription_to_file,
            transcription_result.text,  # Usar el texto del objeto resultado
            output_filename_base,  # Usar el nombre base construido
            config.OUTPUT_TRANSCRIPTS_DIR,
            transcription_request.title,  # Pasar el título original de la petición
        )

        if output_file_path is None:
            logger.error(
                f"CRÍTICO: Fallo al guardar el archivo de transcripción para '{output_filename_base}' en '{config.OUTPUT_TRANSCRIPTS_DIR}'"
            )
            # Limpieza síncrona ya que el guardado final falló.
            files_to_clean_on_save_failure = []
            if video_path_temp:
                files_to_clean_on_save_failure.append(video_path_temp)
            if audio_path_temp:
                files_to_clean_on_save_failure.append(audio_path_temp)

            if files_to_clean_on_save_failure:
                logger.info(
                    f"Ejecutando limpieza síncrona debido a fallo al guardar transcripción para: {files_to_clean_on_save_failure}"
                )
                utils.cleanup_temp_files_sync(files_to_clean_on_save_failure)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor: No se pudo guardar el archivo de transcripción.",
            )

        logger.info(f"Transcripción guardada en: {output_file_path}")

        # 5. Programar limpieza de archivos temporales
        files_to_clean = []
        if video_path_temp:
            files_to_clean.append(video_path_temp)
        if audio_path_temp:
            files_to_clean.append(audio_path_temp)

        if files_to_clean:
            logger.info(f"Programando limpieza en segundo plano para: {files_to_clean}")
            background_tasks.add_task(utils.cleanup_temp_files, files_to_clean)

        # 6. Devolver respuesta de éxito
        preview_text = transcription_result.text  # Usar el texto del objeto resultado
        preview = (
            preview_text[:200] + "..." if len(preview_text) > 200 else preview_text
        )

        # Asegurarse de que output_file_path es un string antes de usar basename
        final_filename = (
            os.path.basename(output_file_path)
            if output_file_path
            else f"{output_filename_base}.txt"
        )

        response_data = TranscriptionResponse(
            message="Transcripción completada exitosamente.",
            filename=final_filename,  # Usar el nombre de archivo base
            original_url=transcription_request.youtube_url,
            transcription_length=len(transcription_result.text),
            detected_language=transcription_result.language,
            transcript_preview=preview,
        )
        return response_data

    except DownloadError as e:
        logger.error(
            f"Fallo en descarga para {transcription_request.youtube_url}: {e}",
            exc_info=True,
        )
        raise e
    except TranscriptionError as e:
        logger.error(
            f"Fallo en transcripción para {transcription_request.youtube_url}: {e}",
            exc_info=True,
        )
        # Limpiar archivos si la transcripción falla pero la descarga tuvo éxito
        files_to_clean_on_transcription_error = [video_path_temp, audio_path_temp]
        if any(
            f
            for f in files_to_clean_on_transcription_error
            if f is not None and os.path.exists(f)
        ):  # Solo limpiar si hay algo que limpiar
            logger.info(
                f"Limpiando archivos temporales después de error de transcripción: {files_to_clean_on_transcription_error}"
            )
            utils.cleanup_temp_files_sync(files_to_clean_on_transcription_error)
        raise e
    except Exception as e:
        logger.critical(
            f"Error inesperado procesando {transcription_request.youtube_url}: {e}",
            exc_info=True,
        )
        # Similar limpieza aquí si es aplicable y los paths son conocidos
        files_to_clean_on_general_error = [video_path_temp, audio_path_temp]
        if any(
            f
            for f in files_to_clean_on_general_error
            if f is not None and os.path.exists(f)
        ):  # Solo limpiar si hay algo que limpiar
            utils.cleanup_temp_files_sync(files_to_clean_on_general_error)
        raise e


# --- Ejemplo de cómo ejecutar con Uvicorn (para desarrollo) ---
# En la terminal, desde el directorio raíz del proyecto (yt-transcription-categorization):
# uvicorn yt_transcriber.main:app --reload
#
# La aplicación estará disponible en http://127.0.0.1:8000
# La documentación interactiva de la API estará en http://127.0.0.1:8000/docs

# (El if __name__ == "__main__": no es la forma idiomática de ejecutar uvicorn para producción,
# pero puede ser útil para pruebas rápidas si no se usa el comando uvicorn directamente)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
