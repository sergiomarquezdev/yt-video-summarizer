# Transcriptor de YouTube a Texto (CLI)

Herramienta simple para descargar videos de YouTube y transcribirlos a texto usando Whisper.

## 1. Requisitos Previos

*   **Python 3.9 o superior.**
*   **ffmpeg**: Necesario para procesar el audio. Asegúrate de que esté instalado y en el PATH de tu sistema.
    *   Puedes descargarlo desde [ffmpeg.org](https://ffmpeg.org/download.html).

## 2. Instalación Rápida

1.  Clona el repositorio:
    ```bash
    # git clone <URL_DEL_REPOSITORIO>
    cd yt-transcription-categorization
    ```
2.  Crea un entorno virtual (recomendado):
    ```bash
    python -m venv venv
    ```
3.  Activa el entorno:
    *   En Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   En macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
4.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## 3. Cómo Usarlo

Para transcribir un video, ejecuta el siguiente comando desde la carpeta del proyecto (`yt-transcription-categorization`):

```bash
python yt_transcriber/cli.py --url "LA_URL_DE_YOUTUBE"
```

*   `--url`: Es la dirección web completa del video de YouTube.

**Ejemplo:**

```bash
python yt_transcriber/cli.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Cuando termine, verás un mensaje como este en la consola, indicando dónde se guardó tu transcripción:

```
Transcripción guardada en: output_transcripts/MiCancionFavorita_vid_dQw4w9WgXcQ_job_20231027123456789012.txt
```
El archivo `.txt` estará en la carpeta `output_transcripts`.

## 4. Opciones Avanzadas (Opcional)

- El título del vídeo se extrae automáticamente de YouTube.
- El idioma se detecta automáticamente por Whisper.

### Variables de entorno configurables

Puedes personalizar el comportamiento de la aplicación mediante variables de entorno (por ejemplo, en un archivo `.env` o exportándolas antes de ejecutar el script). Estas son las variables disponibles:

| Variable                | Valores posibles                                      | Descripción                                                                 |
|-------------------------|------------------------------------------------------|-----------------------------------------------------------------------------|
| `WHISPER_MODEL_NAME`    | `tiny`, `base`, `small`, `medium`, `large`           | Selecciona el modelo de Whisper a usar. Por defecto: `base`.                 |
| `WHISPER_DEVICE`        | `cpu`, `cuda`                                        | Dispositivo para ejecutar Whisper. `cpu` (Por defecto) o `cuda` (usa GPU si está disponible) |
| `TEMP_DOWNLOAD_DIR`     | Ruta (ej: `temp_files/`)                             | Carpeta donde se guardan archivos temporales. Por defecto: `temp_files/`.   |
| `OUTPUT_TRANSCRIPTS_DIR`| Ruta (ej: `output_transcripts/`)                     | Carpeta donde se guardan las transcripciones. Por defecto: `output_transcripts/`. |
| `LOG_LEVEL`             | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`      | Nivel de detalle de los logs. Por defecto: `INFO`.                          |

Puedes crear un archivo `.env` en la raíz del proyecto con el siguiente contenido de ejemplo:

```
WHISPER_MODEL_NAME=base
WHISPER_DEVICE=cpu
TEMP_DOWNLOAD_DIR=temp_files/
OUTPUT_TRANSCRIPTS_DIR=output_transcripts/
LOG_LEVEL=DEBUG
```

## Configuración Avanzada (Opcional)

La aplicación usa configuraciones por defecto para el modelo de Whisper, carpetas temporales, etc. Si necesitas cambiarlas, puedes hacerlo editando el archivo `.env` (crea uno a partir de `.env.example`) o directamente en `yt_transcriber/config.py`.
