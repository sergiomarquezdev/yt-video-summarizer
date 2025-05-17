# YouTube Transcription Service API

## 🚀 Descripción General

Este proyecto proporciona una API FastAPI para descargar el audio de videos de YouTube, transcribirlo a texto utilizando el modelo Whisper de OpenAI y guardar la transcripción en un archivo `.txt`.

La aplicación está diseñada para ser modular y robusta, con un manejo de errores detallado y una configuración flexible.

## ✨ Características Principales

*   **Descarga de Video y Extracción de Audio**: Utiliza `yt-dlp` para descargar eficientemente videos de YouTube y extraer la pista de audio.
*   **Conversión a Formato Estándar**: El audio se convierte a formato WAV, 16kHz, mono, ideal para el procesamiento con Whisper.
*   **Transcripción con Whisper**: Integra `openai-whisper` para una transcripción de audio a texto precisa.
*   **API Asíncrona con FastAPI**: Ofrece un endpoint HTTP robusto y rápido construido con FastAPI.
*   **Normalización de Nombres de Archivo**: Los títulos proporcionados para los archivos de salida se normalizan para asegurar nombres de archivo seguros y consistentes.
*   **Manejo de Archivos Temporales**: Los archivos de video y audio intermedios se almacenan temporalmente y se limpian automáticamente (incluso en caso de error).
*   **Configuración Sencilla**: Parámetros clave como el modelo Whisper y los directorios son configurables.
*   **Logging Detallado**: Registros informativos en cada etapa del proceso para facilitar el seguimiento y la depuración.
*   **Documentación Automática de API**: Gracias a FastAPI, la API ofrece documentación interactiva a través de Swagger UI (`/docs`) y ReDoc (`/redoc`).

## 📋 Requisitos Previos

Antes de ejecutar la aplicación, asegúrate de tener instalado lo siguiente:

1.  **Python**: Versión 3.9 o superior.
2.  **FFmpeg**: Es una dependencia crucial para `yt-dlp` (para la extracción y conversión de audio) y para `openai-whisper` (para cargar diversos formatos de audio). Debes tener `ffmpeg` instalado y accesible en el PATH de tu sistema.
    *   **Windows**: Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y añade la carpeta `bin` a tu variable de entorno PATH.
    *   **macOS**: Puedes instalarlo usando Homebrew: `brew install ffmpeg`
    *   **Linux**: Generalmente disponible a través del gestor de paquetes de tu distribución: `sudo apt update && sudo apt install ffmpeg` (para Debian/Ubuntu) o `sudo yum install ffmpeg` (para Fedora/CentOS).

## ⚙️ Configuración del Proyecto

1.  **Clonar el Repositorio (si aplica)**:
    ```bash
    # git clone <URL_DEL_REPOSITORIO>
    # cd yt-transcription-categorization
    ```

2.  **Crear y Activar un Entorno Virtual (Recomendado)**:
    ```bash
    python -m venv venv
    ```
    *   Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Instalar Dependencias**:
    Asegúrate de que tu entorno virtual esté activado y luego ejecuta:
    ```bash
    pip install -r requirements.txt
    ```
    Para el desarrollo y la ejecución de pruebas de módulos individuales que pueden tener dependencias adicionales (como las pruebas dentro de `yt_transcriber/transcriber.py`), también puedes instalar las dependencias de desarrollo:
    ```bash
    pip install -r requirements-dev.txt
    ```

4.  **Configuraciones (Opcional)**:
    El archivo `yt_transcriber/config.py` contiene las siguientes configuraciones que puedes ajustar:
    *   `WHISPER_MODEL_NAME`: Nombre del modelo Whisper a usar (e.g., "tiny", "base", "small", "medium", "large"). Por defecto es "base". Modelos más grandes son más precisos pero más lentos y consumen más recursos.
    *   `WHISPER_DEVICE`: Dispositivo para ejecutar Whisper ("cpu" o "cuda"). Por defecto es "cpu". Si tienes una GPU NVIDIA compatible y CUDA configurado, puedes cambiarlo a "cuda" para una transcripción significativamente más rápida.
    *   `TEMP_DOWNLOAD_DIR`: Directorio para archivos temporales (video y audio WAV). Por defecto es `"temp_files/"`.
    *   `OUTPUT_TRANSCRIPTS_DIR`: Directorio donde se guardarán las transcripciones `.txt` finales. Por defecto es `"output_transcripts/"`.
    La aplicación creará estos directorios si no existen.

## ▶️ Ejecución de la Aplicación

Con el entorno virtual activado y las dependencias instaladas, puedes iniciar el servidor FastAPI usando Uvicorn desde el directorio raíz del proyecto (`yt-transcription-categorization`):

```bash
uvicorn yt_transcriber.main:app --reload
```

*   `yt_transcriber.main:app`: Apunta al objeto `app` de FastAPI dentro de `yt_transcriber/main.py`.
*   `--reload`: Permite que el servidor se reinicie automáticamente cuando detecta cambios en el código (útil para desarrollo).

Una vez iniciado, la API estará disponible en: `http://127.0.0.1:8000`.

## 🛠️ Uso de la API

La API expone un único endpoint para solicitar transcripciones.

### Endpoint: `POST /transcribe`

Este endpoint procesa una URL de YouTube, descarga el audio, lo transcribe y guarda el resultado.

*   **Método**: `POST`
*   **URL**: `http://127.0.0.1:8000/transcribe`
*   **Cuerpo de la Petición (Request Body)**:
    *   **Formato**: `application/json`
    *   **Campos**:
        *   `youtube_url` (string, formato HttpUrl, requerido): La URL completa del video de YouTube a transcribir.
        *   `title` (string, requerido): Un título sugerido para el archivo de transcripción. Este título será normalizado para crear un nombre de archivo seguro.
    *   **Ejemplo de JSON**:
        ```json
        {
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "title": "Mi Video Favorito de Rick"
        }
        ```

*   **Respuesta Exitosa (Success Response)**:
    *   **Código de Estado**: `200 OK`
    *   **Formato**: `application/json`
    *   **Campos**:
        *   `message` (string): Mensaje de confirmación (ej. "Transcripción completada exitosamente.").
        *   `filename` (string): Nombre del archivo `.txt` donde se guardó la transcripción (ej. `"Mi_Video_Favorito_de_Rick.txt"`).
        *   `original_url` (string): La URL de YouTube que fue procesada.
        *   `transcription_length` (integer): El número de caracteres en el texto transcrito.
        *   `detected_language` (string, opcional): El idioma detectado por Whisper para el audio (ej. "en", "es"). Puede ser `null`.
        *   `transcript_preview` (string, opcional): Una vista previa de los primeros 200 caracteres de la transcripción. Puede ser `null`.
    *   **Ejemplo de JSON de Respuesta Exitosa**:
        ```json
        {
            "message": "Transcripción completada exitosamente.",
            "filename": "Mi_Video_Favorito_de_Rick.txt",
            "original_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "transcription_length": 1856,
            "detected_language": "en",
            "transcript_preview": "We're no strangers to love..."
        }
        ```

*   **Respuestas de Error Comunes**:
    *   **`422 Unprocessable Entity`**: Ocurre si la petición JSON no es válida o falta algún campo requerido (e.g., `youtube_url` no es una URL válida, o `title` está ausente). El cuerpo de la respuesta detallará el error de validación.
        ```json
        {
            "detail": [
                {
                    "loc": ["body", "youtube_url"],
                    "msg": "invalid or missing URL scheme",
                    "type": "value_error.url.scheme"
                }
            ]
        }
        ```
    *   **`503 Service Unavailable`**: Indica un error durante la descarga o extracción de audio del video (controlado por `DownloadError`). Esto puede ocurrir si el video no está disponible, es privado, o `yt-dlp`/`ffmpeg` fallan.
        ```json
        {
            "detail": "Error descargando video: yt-dlp falló: ERROR: [youtube] dQw4w9WgXcQ: Video unavailable. This video is private."
        }
        ```
    *   **`500 Internal Server Error`**: Indica un error durante el proceso de transcripción del audio (controlado por `TranscriptionError`) o cualquier otro error inesperado en el servidor.
        ```json
        {
            "detail": "Error transcribiendo audio: Error inesperado en Whisper: FFmpegsumething went wrong..."
        }
        ```

### Documentación Interactiva de la API

FastAPI genera automáticamente documentación interactiva para la API. Puedes acceder a ella a través de tu navegador una vez que el servidor esté en funcionamiento:

*   **Swagger UI**: `http://127.0.0.1:8000/docs`
*   **ReDoc**: `http://127.0.0.1:8000/redoc`

Estas interfaces te permiten explorar el endpoint, ver los modelos de datos y probar la API directamente desde el navegador.

## 📂 Estructura del Proyecto

```
yt-transcription-categorization/
├── .cursor/
│   ├── notes/
│   │   ├── PLAN.md             # Plan de desarrollo inicial.
│   │   └── analysis_notes.md   # Notas de análisis de documentos de referencia.
│   └── yt_transcriber_test/
│       └── TEST.md             # Casos de prueba detallados.
├── temp_files/                 # Directorio temporal para videos y audios (creado dinámicamente).
├── output_transcripts/         # Directorio para las transcripciones .txt (creado dinámicamente).
├── yt_transcriber/             # Módulo principal de la aplicación.
│   ├── __init__.py
│   ├── main.py                 # Lógica del servidor FastAPI y endpoint.
│   ├── downloader.py           # Descarga de video y extracción de audio.
│   ├── transcriber.py          # Transcripción de audio con Whisper.
│   ├── utils.py                # Funciones de utilidad (manejo de archivos, normalización).
│   └── config.py               # Configuraciones de la aplicación.
├── .gitignore
├── .python-version             # Versión de Python (para pyenv).
├── README.md                   # Este archivo.
└── requirements.txt            # Dependencias del proyecto.
```

## 🌊 Flujo de Trabajo Simplificado

1.  **Petición HTTP POST** llega a `/transcribe` con `youtube_url` y `title`.
2.  **Validación Pydantic**: FastAPI valida los datos de entrada.
3.  **Normalización de Título**: `main.py` usa `utils.normalize_title_for_filename()`.
4.  **Descarga y Extracción**: `main.py` llama a `downloader.download_and_extract_audio()`.
    *   `yt-dlp` descarga el video.
    *   `ffmpeg` (vía `yt-dlp`) extrae el audio a WAV (16kHz, mono) en `temp_files/`.
5.  **Transcripción**: `main.py` llama a `transcriber.transcribe_audio_file()`.
    *   El modelo Whisper se carga (o se reutiliza desde caché).
    *   El archivo WAV se transcribe a texto.
6.  **Guardado de Transcripción**: `main.py` llama a `utils.save_transcription_to_file()`.
    *   El texto se guarda en `output_transcripts/{normalized_title}.txt`.
7.  **Respuesta HTTP**: Se envía una respuesta JSON `200 OK` con detalles.
8.  **Limpieza (Background)**: `main.py` programa `utils.cleanup_temp_files()` con `BackgroundTasks` para eliminar los archivos de `temp_files/`.
9.  **Manejo de Errores**: Si ocurre un error en cualquier etapa, se captura, se loguea, se realiza una limpieza síncrona de archivos temporales (si aplica) y se devuelve una respuesta HTTP de error apropiada (422, 500, 503).

## ⚠️ Consideraciones Adicionales

*   **Dependencia de FFmpeg**: La correcta instalación y accesibilidad de FFmpeg en el PATH del sistema es crucial.
*   **Rendimiento de Whisper**: El modelo "base" es relativamente rápido en CPU. Para audios largos o si se usan modelos más grandes sin GPU, la transcripción puede tomar un tiempo considerable. Las operaciones de descarga y transcripción se ejecutan en un `threadpool` para no bloquear el servidor FastAPI, pero las peticiones se procesarán secuencialmente si el pool es limitado y las tareas son largas.
*   **Concurrencia**: El sistema está diseñado para manejar múltiples peticiones. Los nombres de archivo de salida son únicos si los `title` de entrada lo son. La carga del modelo Whisper tiene una caché simple; en escenarios de muy alta concurrencia con modelos variables, podrían considerarse mecanismos de bloqueo más explícitos para la carga del modelo.

## 🚀 Futuras Implementaciones (Posibles Mejoras)

*   Permitir la selección del modelo Whisper y el idioma a través de la petición API.
*   Soporte para otros formatos de salida (ej. JSON con timestamps, SRT, VTT).
*   Integración con una base de datos para almacenar metadatos y transcripciones.
*   Un frontend simple para interactuar con la API.
*   Mejoras en la gestión de la caché del modelo Whisper para entornos de alta concurrencia.

---

Este `README.md` busca ser completo y profesional. ¡Espero que te sea de utilidad!
