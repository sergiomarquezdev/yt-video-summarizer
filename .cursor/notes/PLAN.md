# Plan de Acción: Transcriptor de YouTube a Texto

## Objetivo Principal
Desarrollar una aplicación Python que actúe como un servicio (endpoint HTTP con FastAPI) para:
1.  Recibir una URL de YouTube y un título a través de una petición JSON.
2.  Descargar el video de la URL proporcionada.
3.  Extraer la pista de audio en formato WAV (16kHz, mono).
4.  Transcribir el audio a texto plano utilizando `openai-whisper`.
5.  Guardar la transcripción en un archivo `.txt` utilizando el título proporcionado como nombre de archivo (normalizado).
6.  Eliminar los archivos temporales (video y audio) después del procesamiento.
7.  Asegurar un manejo robusto de errores durante todo el proceso.

## Fases del Proyecto (Checklist)

- [x] **Fase 1: Configuración del Entorno y Estructura del Proyecto**
  - [x] **Tarea 1.1**: Crear la estructura básica de directorios del proyecto.
    - [x] `yt_transcriber/` (directorio principal de la aplicación)
      - [x] `main.py` (contendrá la lógica del endpoint FastAPI y orquestación)
      - [x] `downloader.py` (módulo para descarga y extracción de audio)
      - [x] `transcriber.py` (módulo para la transcripción de audio)
      - [x] `config.py` (para configuraciones como el modelo Whisper, directorio temporal)
      - [x] `utils.py` (para funciones de utilidad, como la limpieza de archivos)
      - [x] `output_transcripts/` (directorio para guardar los archivos .txt resultantes) - *Se creará dinámicamente*
    - [x] `requirements.txt` (listado de dependencias)
    - [x] `README.md` (instrucciones de configuración y uso)
    - [x] `.gitignore`
  - [x] **Tarea 1.2**: Definir y listar las dependencias en `requirements.txt`.
    - [x] `yt-dlp`
    - [x] `openai-whisper`
    - [x] `torch`
    - [x] `fastapi`
    - [x] `uvicorn[standard]`
    - [x] `python-dotenv` (opcional, no añadido activamente)
  - [x] **Tarea 1.3**: Crear archivo `config.py`.
    - [x] Definir variables de configuración:
      - [x] `WHISPER_MODEL_NAME = "base"`
      - [x] `WHISPER_DEVICE = "cpu"`
      - [x] `TEMP_DOWNLOAD_DIR = "temp_files/"`
      - [x] `OUTPUT_TRANSCRIPTS_DIR = "output_transcripts/"`
  - [x] **Tarea 1.4**: (Opcional Futuro - Anotado) Crear sección en `README.md`.
    - [x] Guardar salida en base de datos.
    - [x] Permitir configuración de ubicación de archivos temporales y de salida.
    - [x] Posibles formatos de salida estructurados.

- [x] **Fase 2: Implementación del Módulo de Descarga (`downloader.py`)**
  - [x] **Tarea 2.1**: Crear la función `download_and_extract_audio` (ahora lanza `DownloadError`).

- [x] **Fase 3: Implementación del Módulo de Transcripción (`transcriber.py`)**
  - [x] **Tarea 3.1**: Crear la función `transcribe_audio_file` (ahora devuelve `TranscriptionResult` o lanza `TranscriptionError`).

- [x] **Fase 4: Implementación de Utilidades (`utils.py`)**
  - [x] **Tarea 4.1**: Crear la función `save_transcription_to_file`.
  - [x] **Tarea 4.2**: Crear la función `cleanup_temp_files`.
  - [x] **Tarea 4.3**: Crear la función `ensure_dir_exists`.
  - [x] **Tarea 4.4**: (Implícitamente añadida) Crear `normalize_title_for_filename`.
  - [x] **Tarea 4.5**: (Implícitamente añadida) Crear `cleanup_temp_files_sync`.

- [x] **Fase 5: Implementación del Endpoint y Orquestación (`main.py` con FastAPI)**
  - [x] **Tarea 5.1**: Configurar la aplicación FastAPI en `main.py`.
  - [x] **Tarea 5.2**: Definir modelos Pydantic para la petición y respuesta.
  - [x] **Tarea 5.3**: Crear un endpoint (`/transcribe`) que acepte peticiones POST.
  - [x] **Tarea 5.4**: Lógica del endpoint (con todas las llamadas a sub-módulos y manejo de `TranscriptionResult`).
  - [x] **Tarea 5.5**: Implementar manejo de errores usando `HTTPException`, excepciones personalizadas y limpieza síncrona/asíncrona.
  - [x] **Tarea 5.6**: Configurar Uvicorn para ejecutar la aplicación.

- [x] **Fase 6: Pruebas y Documentación** (En progreso)
  - [x] **Tarea 6.1**: Probar el endpoint (Cubierto por pruebas manuales y análisis exhaustivo).
  - [x] **Tarea 6.2**: Probar el manejo de errores (Cubierto por análisis exhaustivo y plan de pruebas `TEST.md`).
  - [x] **Tarea 6.3**: Actualizar y completar el `README.md` con documentación profesional.
    - [x] Instrucciones detalladas de configuración (incluyendo `ffmpeg`).
    - [x] Cómo instalar dependencias.
    - [x] Cómo ejecutar la aplicación.
    - [x] Ejemplo de cómo llamar al endpoint.
    - [x] Mencionar la documentación automática de la API.
    - [x] Estructura del proyecto.
  - [x] **Tarea 6.4**: Revisar el código para claridad, modularidad y adherencia a PEP 8 (Realizado progresivamente).
  - [x] **Tarea 6.5**: (Implícitamente añadida) Crear y mantener plan de pruebas `TEST.md`.

- [x] **Fase 7: Refinamiento y Mejoras Incrementales** (Basado en `initial_review_suggestions.md`)
  - [x] **Tarea 7.1**: Separar dependencias de desarrollo (`numpy`, `soundfile`) a `requirements-dev.txt`.
  - [x] **Tarea 7.2**: Refinar la lógica de manejo de errores en la descarga (`main.py`), enfocándose en la validación de `audio_path_temp`.
  - [x] **Tarea 7.3**: Optimizar carga del modelo Whisper:
    - [x] Considerar cargar el modelo Whisper durante el evento de inicio (`startup`) de FastAPI para reducir latencia en la primera petición.
  - [x] **Tarea 7.4**: Mejorar la unicidad de los nombres de archivo temporales y de salida:
    - [x] Investigar y potencialmente añadir un UUID corto o timestamp a los nombres de archivo para evitar colisiones en alta concurrencia.
  - [x] **Tarea 7.5**: Mejorar la gestión de la configuración:
    - [x] Integrar `python-dotenv` para permitir la configuración mediante variables de entorno, complementando `config.py`.

- [x] **Fase 8: Revisión y Limpieza Exhaustiva del Código**
  - [x] **Tarea 8.1**: Realizar una revisión detallada y limpieza de comentarios, código innecesario y logs en todos los módulos principales (`config.py`, `downloader.py`, `transcriber.py`, `utils.py`, `main.py`).
    - [x] Primera pasada de limpieza y refactorización.
    - [x] Segunda pasada de revisión y pulido final.

- [ ] **Fase 9: Refinamiento Post-Testing y Mejoras Arquitectónicas**
    - [x] **Tarea 9.1 (CRÍTICO - TC_018):** Mejorar el manejo de errores en `main.py` cuando `utils.save_transcription_to_file` falla.
        - [x] Verificar si `output_file_path` es `None`.
        - [x] Si es `None`, registrar error crítico.
        - [x] Si es `None`, ejecutar limpieza síncrona de archivos temporales (`video_path_temp`, `audio_path_temp`).
        - [x] Si es `None`, lanzar `HTTPException 500`.
    - [x] **Tarea 9.3: Mejoras en `yt_transcriber/config.py`**
        - [x] (Opcional) Considerar validación de variables de configuración al inicio (ej. con Pydantic).
        - [x] Asegurar tipado claro para todas las configuraciones si se vuelven más complejas.
    - [x] **Tarea 9.4: Mejoras en `yt_transcriber/downloader.py`**
        - [x] Revisar periódicamente las opciones de `yt-dlp` para optimizaciones (revisado, sin cambios urgentes).
        - [x] Asegurar que el nivel de logging de la aplicación permita ver logs detallados de `yt-dlp` para depuración (implementado nivel de log configurable).
    - [x] **Tarea 9.5: Mejoras en `yt_transcriber/transcriber.py`**
        - [x] Considerar hacer parametrizables las `DecodingOptions` de Whisper (idioma, timestamps) si se requiere flexibilidad futura. (Implementado para `language` y `include_timestamps`)
    - [x] **Tarea 9.7: Mejoras en `yt_transcriber/main.py` (adicionales a Tarea 9.2)**
        - [x] (Opcional) Considerar estandarizar un formato de respuesta de error más rico para `500/503` si la API crece. (Implementado con ApiErrorDetail y handlers globales)
