# Notas del Análisis para la Aplicación de Transcripción de YouTube

## Resumen General

El objetivo es crear una aplicación Python que:
1.  Tome una URL de YouTube como entrada.
2.  Descargue el video.
3.  Extraiga la pista de audio.
4.  Transcriba el audio a texto plano.
5.  Devuelva el texto plano.

## Componentes Clave y Flujo (basado en los documentos)

### 1. Descarga de Video y Extracción de Audio

*   **Herramienta Principal**: `yt-dlp` (Python library).
    *   Referencia: `youtube_integration_guide.md`, `video_download_process.md`.
*   **Proceso**:
    *   Utilizar `yt-dlp` para descargar el video (preferiblemente en formato MP4).
        *   Opción `format`: `bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4` o similar para obtener MP4.
        *   Opción `outtmpl`: Para controlar la plantilla del nombre de archivo de salida.
    *   Utilizar `yt-dlp` con post-procesadores (`FFmpegExtractAudio`) para extraer el audio.
        *   Formato de audio: WAV.
        *   Especificaciones de audio: 16kHz, mono. (Argumentos para `FFmpegExtractAudio`: `["-ar", "16000", "-ac", "1"]`).
        *   Opción `keepvideo: True`: Para conservar el archivo de video después de la extracción de audio.
*   **Gestión de Archivos**:
    *   Se necesitará un directorio temporal para almacenar el video descargado y el archivo de audio extraído.
    *   Considerar la limpieza de estos archivos después del procesamiento.
*   **Metadatos**:
    *   `yt-dlp` puede extraer metadatos ricos (título, duración, etc.). Aunque para esta aplicación simple, el foco principal es la transcripción, podríamos guardar el título para asociarlo con la transcripción.
*   **Módulos de Referencia (del proyecto Vitaly Academy)**:
    *   `src/download_videos_yt.py` (contiene la lógica de `process_youtube_video`, `_download_video_and_extract_audio`).
    *   `youtube_integration_guide.md` (proporciona ejemplos de código para `download_youtube_video`).

### 2. Transcripción de Audio

*   **Herramienta Principal**: `openai-whisper`.
    *   Referencia: `audio_narration_processing.md`.
*   **Proceso**:
    *   Cargar el modelo Whisper (configurable, e.g., "base", "small", "medium").
        *   Configuración: `WHISPER_MODEL` y `WHISPER_DEVICE` (cpu/cuda) - se puede gestionar con un archivo de configuración simple o variables de entorno.
    *   Pasar la ruta del archivo WAV (16kHz, mono) al método `transcribe` del modelo.
    *   Extraer el texto de la transcripción del resultado (`result["text"]`).
*   **Módulos de Referencia (del proyecto Vitaly Academy)**:
    *   `src/utils_narracion.py` (contiene la lógica `transcribe_audio`).

### 3. Flujo General de la Aplicación Propuesta

1.  Función principal que acepta una URL de YouTube.
2.  Llamar a una función de descarga y extracción de audio:
    *   Input: URL de YouTube, directorio de salida temporal.
    *   Output: Ruta al archivo WAV.
3.  Llamar a una función de transcripción:
    *   Input: Ruta al archivo WAV.
    *   Output: Texto de la transcripción.
4.  Devolver el texto de la transcripción.
5.  (Opcional) Limpiar archivos temporales.

## Consideraciones Adicionales (basadas en guías y buenas prácticas)

*   **Manejo de Errores**: Implementar `try-except` bloques para manejar errores durante la descarga (e.g., `yt_dlp.utils.DownloadError`) y la transcripción.
*   **Configuración**: Para el modelo Whisper (nombre, dispositivo) y quizás rutas temporales. Un archivo `config.py` o `settings.json` simple, o incluso argumentos de línea de comandos para la aplicación principal.
*   **Dependencias**:
    *   `yt-dlp`
    *   `openai-whisper`
    *   `torch` (dependencia de Whisper)
    *   `ffmpeg` (necesita estar instalado en el sistema y accesible en el PATH, ya que `yt-dlp` y Whisper lo utilizan).
*   **Estructura del Proyecto (Simple)**:
    *   `main.py` (o `transcriber.py`): Script principal.
    *   `downloader.py`: Módulo para la lógica de descarga y extracción de audio.
    *   `transcriber_module.py`: Módulo para la lógica de transcripción.
    *   `config.py` (opcional): Para configuraciones.
    *   `requirements.txt`: Para dependencias.
    *   `README.md`: Instrucciones de uso.
*   **Salida**: Texto plano. Más adelante se podría considerar estructurar la salida, pero por ahora es texto plano.

## Puntos a Omitir (de los documentos de Vitaly Academy para esta aplicación más simple)

*   Integración con Pub/Sub.
*   Interacción con base de datos PostgreSQL.
*   Detección de música (Demucs), VAD (Silero VAD).
*   Clasificación de contenido con GPT.
*   La compleja estructura de directorios y módulos de Vitaly Academy (se simplificará).
*   Manejo de múltiples fuentes de video (Vimeo).

Este análisis inicial cubre los aspectos fundamentales.
