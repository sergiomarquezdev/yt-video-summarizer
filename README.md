# Transcriptor de YouTube a Texto (CLI)

Herramienta CLI para descargar videos de YouTube y transcribirlos a texto usando [OpenAI's Whisper](https://github.com/openai/whisper).

## 1. Requisitos Previos

- **Python 3.9 o superior.**
- **ffmpeg**: Necesario para el procesamiento de audio. Asegúrate de que esté instalado y disponible en el PATH de tu sistema.
  - Puedes descargarlo desde [ffmpeg.org](https://ffmpeg.org/download.html).

## 2. Instalación

1.  **Clona el repositorio:**

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd yt-video-summarizer
    ```

2.  **Crea y activa un entorno virtual (recomendado):**

    ```bash
    python -m venv venv
    ```

    - En Windows:
      ```bash
      venv\Scripts\activate
      ```
    - En macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## 3. Cómo Usarlo

Para transcribir un video, ejecuta el siguiente comando desde la raíz del proyecto:

```bash
python -m yt_transcriber.cli --url "LA_URL_DE_YOUTUBE" [--language "CODIGO_IDIOMA"]
```

- `--url` / `-u`: **(Obligatorio)** La dirección web completa del video de YouTube.
- `--language` / `-l`: **(Opcional)** El código del idioma (ej. `en`, `es`, `fr`) para forzar la transcripción en ese idioma. Si no se especifica, Whisper lo detectará automáticamente.

### Ejemplos

- **Detección automática de idioma:**

  ```bash
  python -m yt_transcriber.cli -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  ```

- **Forzar transcripción en español:**
  ```bash
  python -m yt_transcriber.cli -u "https://www.youtube.com/watch?v=video_en_otro_idioma" -l "es"
  ```

Al finalizar, la consola indicará la ruta donde se guardó el archivo de transcripción:

```
Transcripción guardada en: output_transcripts/MiVideo_vid_VIDEO_ID_job_20231028123456.txt
```

## 4. Funcionamiento

- **Título del Video**: El título se extrae automáticamente de YouTube para nombrar el archivo de salida de forma descriptiva.
- **Detección de Idioma**: Por defecto, Whisper detecta automáticamente el idioma del audio. Puedes forzar un idioma específico usando el argumento `--language` (o `-l`), lo cual puede mejorar la precisión si el idioma es conocido.
- **Archivos de Salida**: Las transcripciones se guardan en la carpeta `output_transcripts/`. El nombre del archivo incluye el título del video, su ID y un identificador único del proceso para evitar colisiones.
- **Archivos Temporales**: Los videos y audios descargados se almacenan temporalmente en una subcarpeta única dentro de `temp_files/` y se eliminan automáticamente al finalizar el proceso.

## 5. Configuración

Puedes personalizar el comportamiento de la aplicación mediante variables de entorno. La forma más sencilla es crear un archivo `.env` en la raíz del proyecto.

Estas son las variables disponibles:

| Variable                 | Valores posibles                                | Descripción                                                                           |
| ------------------------ | ----------------------------------------------- | ------------------------------------------------------------------------------------- |
| `WHISPER_MODEL_NAME`     | `tiny`, `base`, `small`, `medium`, `large`      | Selecciona el modelo de Whisper a usar. Por defecto: `base`.                          |
| `WHISPER_DEVICE`         | `cpu`, `cuda`                                   | Dispositivo para ejecutar Whisper. `cpu` (Por defecto) o `cuda` (si está disponible). |
| `TEMP_DOWNLOAD_DIR`      | Ruta (ej: `temp_files/`)                        | Carpeta donde se guardan archivos temporales. Por defecto: `temp_files/`.             |
| `OUTPUT_TRANSCRIPTS_DIR` | Ruta (ej: `output_transcripts/`)                | Carpeta donde se guardan las transcripciones. Por defecto: `output_transcripts/`.     |
| `LOG_LEVEL`              | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | Nivel de detalle de los logs en consola. Por defecto: `INFO`.                         |

**Ejemplo de archivo `.env`:**

```
WHISPER_MODEL_NAME=small
WHISPER_DEVICE=cuda
LOG_LEVEL=DEBUG
```
