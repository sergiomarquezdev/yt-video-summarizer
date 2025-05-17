# Transcriptor de YouTube a Texto (CLI)

Esta aplicación es una herramienta de línea de comandos (CLI) que descarga videos de YouTube, extrae el audio y lo transcribe a texto plano utilizando el modelo Whisper de OpenAI.

## Características

*   Descarga de video y extracción de audio desde URLs de YouTube (`yt-dlp`).
*   Transcripción de audio a texto (`openai-whisper`).
*   Nombres de archivo de salida personalizables basados en el título proporcionado.
*   Limpieza automática de archivos temporales.
*   Configurable a través de variables de entorno (ver `yt_transcriber/config.py` y `.env.example`).
*   Opción para especificar idioma de transcripción y si se incluyen timestamps (pasados a Whisper).

## Requisitos Previos

*   Python 3.9 o superior.
*   `ffmpeg` instalado y accesible en el PATH del sistema. `yt-dlp` lo requiere para la extracción y conversión de audio. Puedes descargarlo desde [ffmpeg.org](https://ffmpeg.org/download.html).

## Configuración

1.  **Clona el repositorio (si aplica):**
    ```bash
    git clone <tu-repositorio-url>
    cd yt-transcription-categorization
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    Si tienes `requirements-dev.txt` y quieres instalar dependencias de desarrollo (como `numpy`, `soundfile` para pruebas directas de módulos antiguos):
    ```bash
    pip install -r requirements-dev.txt
    ```

4.  **Configuración del Entorno (Opcional):**
    Puedes configurar la aplicación creando un archivo `.env` en la raíz del proyecto. Copia el archivo `.env.example` a `.env` y ajusta las variables según sea necesario:
    ```bash
    cp .env.example .env
    ```
    Variables configurables:
    *   `WHISPER_MODEL_NAME`: Modelo de Whisper a usar (ej. "tiny", "base", "small", "medium", "large"). Por defecto: "base".
    *   `WHISPER_DEVICE`: Dispositivo para correr Whisper (ej. "cpu", "cuda"). Por defecto: "cpu".
    *   `TEMP_DOWNLOAD_DIR`: Directorio para archivos temporales. Por defecto: "temp_files/".
    *   `OUTPUT_TRANSCRIPTS_DIR`: Directorio para las transcripciones finales. Por defecto: "output_transcripts/".
    *   `LOG_LEVEL`: Nivel de logging (ej. "INFO", "DEBUG"). Por defecto: "INFO".

## Uso

Ejecuta el script `cli.py` desde el directorio raíz del proyecto, proporcionando la URL del video de YouTube y un título para el archivo de salida.

```bash
python yt_transcriber/cli.py --url "URL_DEL_VIDEO_DE_YOUTUBE" --title "Titulo Para El Archivo"
```

**Argumentos:**

*   `-u URL, --url URL` (Obligatorio): La URL completa del video de YouTube.
    *   Ejemplo: `"https://www.youtube.com/watch?v=dQw4w9WgXcQ"`
*   `-t TITULO, --title TITULO` (Obligatorio): El título base que se usará para nombrar el archivo de transcripción `.txt` resultante. Se normalizará para eliminar caracteres no válidos para nombres de archivo.
    *   Ejemplo: `"Mi Video Favorito Transcrito"`
*   `-l IDIOMA, --language IDIOMA` (Opcional): Código de idioma de dos letras (ej. "en", "es", "fr") para forzar la transcripción en ese idioma. Si no se especifica, Whisper intentará detectar el idioma automáticamente.
    *   Ejemplo: `--language es`
*   `--include_timestamps` (Opcional): Si se incluye este flag, se pasarán las opciones a Whisper para que intente generar timestamps. (La salida en el archivo .txt seguirá siendo texto plano por ahora).

**Ejemplo Completo:**

```bash
python yt_transcriber/cli.py --url "https://www.youtube.com/watch?v=Y-Jy_ClFIos" --title "Test Video Español" --language es
```

Esto procesará el video, y si tiene éxito, imprimirá en la consola la ruta al archivo `.txt` guardado en el directorio `output_transcripts/` (o el configurado). El nombre del archivo incluirá el título normalizado, el ID del video y un ID de trabajo único.

**Salida en caso de éxito:**

```
Transcripción guardada en: output_transcripts/Test_Video_Espanol_vid_Y-Jy_ClFIos_job_20231027123456789012.txt
```

En caso de error, se mostrarán mensajes en la consola.

## Estructura del Proyecto

```
yt-transcription-categorization/
├── yt_transcriber/ # Código fuente de la aplicación
│   ├── __init__.py
│   ├── cli.py              # Punto de entrada para la interfaz de línea de comandos
│   ├── config.py           # Gestión de configuración (lee .env)
│   ├── downloader.py       # Lógica para descargar videos y extraer audio
│   ├── transcriber.py      # Lógica para la transcripción de audio con Whisper
│   └── utils.py            # Funciones de utilidad (normalización, limpieza, etc.)
├── .env.example            # Ejemplo de archivo de configuración de entorno
├── .gitignore
├── .python-version         # (Si usas pyenv)
├── README.md               # Este archivo
├── requirements-dev.txt    # Dependencias para desarrollo/pruebas
└── requirements.txt        # Dependencias principales
```

## Posibles Mejoras Futuras

*   Opción para especificar el formato de salida de la transcripción (ej. JSON con timestamps, SRT, VTT).
*   Añadir la opción `--retain-video-file` al CLI para conservar el archivo de video descargado.
*   Integración con una base de datos para almacenar metadatos y transcripciones.
*   Mejoras en el empaquetado para una distribución más fácil (ej. usando `setuptools` y creando un paquete instalable).

---

Este `README.md` busca ser completo y profesional. ¡Espero que te sea de utilidad!
