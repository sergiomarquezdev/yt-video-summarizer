# Plan de Acción: Transcriptor de YouTube a Texto

## Objetivo Principal
Desarrollar una aplicación Python que actúe como una herramienta de línea de comandos (CLI) para:
1.  Recibir una URL de YouTube y un título a través de parámetros de línea de comandos.
2.  Descargar el video de la URL proporcionada.
3.  Extraer la pista de audio en formato WAV (16kHz, mono).
4.  Transcribir el audio a texto plano utilizando `openai-whisper`.
5.  Guardar la transcripción en un archivo `.txt` utilizando el título proporcionado como nombre de archivo (normalizado).
6.  Eliminar los archivos temporales (video y audio) después del procesamiento.
7.  Asegurar un manejo robusto de errores durante todo el proceso e informar al usuario a través de la consola.

## Fases del Proyecto (Checklist)

- [x] **Fase 1: Configuración del Entorno y Estructura del Proyecto (API Inicial)**
  - [x] **Tarea 1.1**: Crear la estructura básica de directorios del proyecto.
    - [x] `yt_transcriber/` (directorio principal de la aplicación)
      - [x] `main.py` (lógica inicial del endpoint FastAPI y orquestación)
      - [x] `downloader.py` (módulo para descarga y extracción de audio)
      - [x] `transcriber.py` (módulo para la transcripción de audio)
      - [x] `config.py` (para configuraciones como el modelo Whisper, directorio temporal)
      - [x] `utils.py` (para funciones de utilidad, como la limpieza de archivos)
      - [x] `output_transcripts/` (directorio para guardar los archivos .txt resultantes) - *Creado dinámicamente*
    - [x] `requirements.txt` (listado de dependencias)
    - [x] `README.md` (instrucciones de configuración y uso)
    - [x] `.gitignore`
  - [x] **Tarea 1.2**: Definir y listar las dependencias en `requirements.txt`.
    - [x] `yt-dlp`
    - [x] `openai-whisper`
    - [x] `torch`
    - [x] `fastapi` (para la versión API inicial)
    - [x] `uvicorn[standard]` (para la versión API inicial)
    - [x] `python-dotenv`
    - [x] `pydantic`
  - [x] **Tarea 1.3**: Crear archivo `config.py`.
    - [x] Definir variables de configuración.
  - [x] **Tarea 1.4**: (Opcional Futuro - Anotado) Crear sección en `README.md`.
    - [x] Guardar salida en base de datos.
    - [x] Permitir configuración de ubicación de archivos temporales y de salida.
    - [x] Posibles formatos de salida estructurados.

- [x] **Fase 2: Implementación del Módulo de Descarga (`downloader.py`)**
  - [x] **Tarea 2.1**: Crear la función `download_and_extract_audio`.

- [x] **Fase 3: Implementación del Módulo de Transcripción (`transcriber.py`)**
  - [x] **Tarea 3.1**: Crear la función `transcribe_audio_file`.

- [x] **Fase 4: Implementación de Utilidades (`utils.py`)**
  - [x] **Tarea 4.1**: Crear la función `save_transcription_to_file`.
  - [x] **Tarea 4.2**: Crear la función `cleanup_temp_files` (posteriormente `cleanup_temp_files_sync`).
  - [x] **Tarea 4.3**: Crear la función `ensure_dir_exists`.
  - [x] **Tarea 4.4**: Crear `normalize_title_for_filename`.
  - [x] **Tarea 4.5**: Crear `cleanup_temp_files_sync`.

- [x] **Fase 5: Implementación del Endpoint y Orquestación (`main.py` con FastAPI - Versión API)**
  - [x] **Tarea 5.1**: Configurar la aplicación FastAPI en `main.py`.
  - [x] **Tarea 5.2**: Definir modelos Pydantic para la petición y respuesta.
  - [x] **Tarea 5.3**: Crear un endpoint (`/transcribe`).
  - [x] **Tarea 5.4**: Lógica del endpoint.
  - [x] **Tarea 5.5**: Implementar manejo de errores y limpieza.
  - [x] **Tarea 5.6**: Configurar Uvicorn para ejecutar la aplicación.

- [x] **Fase 6: Pruebas y Documentación (Versión API)**
  - [x] **Tarea 6.1**: Probar el endpoint.
  - [x] **Tarea 6.2**: Probar el manejo de errores.
  - [x] **Tarea 6.3**: Actualizar y completar el `README.md` para la versión API.
  - [x] **Tarea 6.4**: Revisar el código para claridad, modularidad y adherencia a PEP 8.
  - [x] **Tarea 6.5**: Crear y mantener plan de pruebas `TEST.md` para la versión API.

- [x] **Fase 7: Refinamiento y Mejoras Incrementales (Versión API)**
  - [x] **Tarea 7.1**: Separar dependencias de desarrollo a `requirements-dev.txt`.
  - [x] **Tarea 7.2**: Refinar la lógica de manejo de errores en la descarga.
  - [x] **Tarea 7.3**: Optimizar carga del modelo Whisper (carga al inicio).
  - [x] **Tarea 7.4**: Mejorar la unicidad de los nombres de archivo (uso de `job_id`).
  - [x] **Tarea 7.5**: Mejorar la gestión de la configuración (`python-dotenv`).

- [x] **Fase 8: Revisión y Limpieza Exhaustiva del Código (Versión API)**
  - [x] **Tarea 8.1**: Realizar una revisión detallada y limpieza de todos los módulos.

- [x] **Fase 9: Refinamiento Post-Testing y Mejoras Arquitectónicas (Versión API)**
    - [x] **Tarea 9.1 (CRÍTICO - TC_018):** Mejorar el manejo de errores en `main.py` cuando `utils.save_transcription_to_file` falla.
    - [-] **Tarea 9.2 (ARQUITECTURA - TC_016):** Diseñar e implementar una arquitectura de procesamiento asíncrono.
        - [-] *Esta tarea se considera **NO APLICABLE/POSPUESTA** para la versión CLI actual, dado el enfoque en uso local y personal.*
    - [x] **Tarea 9.3: Mejoras en `yt_transcriber/config.py`**
        - [x] (Opcional) Validación de variables de configuración con Pydantic (implementado).
        - [x] Tipado claro para configuraciones (implementado).
    - [x] **Tarea 9.4: Mejoras en `yt_transcriber/downloader.py`**
        - [x] Revisión de opciones de `yt-dlp` (realizado).
        - [x] Logging detallado de `yt-dlp` (implementado).
    - [x] **Tarea 9.5: Mejoras en `yt_transcriber/transcriber.py`**
        - [x] Parametrización de `DecodingOptions` de Whisper (implementado).
    - [x] **Tarea 9.7: Mejoras en `yt_transcriber/main.py`**
        - [x] (Opcional) Formato de respuesta de error más rico (implementado en versión API).

- [x] **Fase 10: Refactorización a Aplicación de Línea de Comandos (CLI)**
    - [x] **Tarea 10.1**: Crear `yt_transcriber/cli.py` con `argparse`.
        - [x] Definir argumentos: `--url`, `--title`, `--language`, `--include_timestamps`.
        - [x] Adaptar la lógica de procesamiento principal de `main.py` a `cli.py`.
    - [x] **Tarea 10.2**: Modificar la carga del modelo Whisper para el contexto CLI.
        - [x] Cargar el modelo globalmente al inicio del script o antes del primer procesamiento.
    - [x] **Tarea 10.3**: Adaptar el manejo de errores y la salida.
        - [x] Usar `print` para mensajes al usuario (stdout/stderr).
        - [x] Usar `sys.exit()` con códigos de estado apropiados.
        - [x] Asegurar limpieza síncrona de archivos temporales en todos los casos.
    - [x] **Tarea 10.4**: Actualizar `requirements.txt`.
        - [x] Eliminar `fastapi` y `uvicorn`.
    - [x] **Tarea 10.5**: Actualizar `README.md` para reflejar el uso CLI.
        - [x] Nuevas instrucciones de instalación y ejecución.
        - [x] Descripción de argumentos CLI.
        - [x] Actualización de la estructura del proyecto.
    - [x] **Tarea 10.6 (Opcional pero recomendado)**: Eliminar `yt_transcriber/main.py` ya que su funcionalidad ha sido reemplazada por `cli.py`. *(Pendiente de tu confirmación)*

## Tareas Pendientes / Próximos Pasos

- Confirmar la eliminación de `yt_transcriber/main.py` (Tarea 10.6).
- Revisar y adaptar `TEST.md` para la versión CLI.
- Considerar las "Posibles Mejoras Futuras" listadas en el `README.md` si el proyecto evoluciona.
