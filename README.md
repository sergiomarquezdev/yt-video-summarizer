# Transcriptor de YouTube a Texto (CLI)

Herramienta simple para descargar videos de YouTube y transcribirlos a texto usando Whisper.

## 1. Requisitos Previos

*   **Python 3.9 o superior.**
*   **ffmpeg**: Necesario para procesar el audio. Asegúrate de que esté instalado y en el PATH de tu sistema.
    *   Puedes descargarlo desde [ffmpeg.org](https://ffmpeg.org/download.html).

## 2. Instalación Rápida

1.  Clonar el repositorio:
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
python yt_transcriber/cli.py --url "LA_URL_DE_YOUTUBE" --title "EL_TITULO_PARA_TU_ARCHIVO"
```

*   `--url`: Es la dirección web completa del video de YouTube.
*   `--title`: Es el nombre que quieres darle al archivo de texto que se creará.

**Ejemplo:**

```bash
python yt_transcriber/cli.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --title "MiCancionFavorita"
```

Cuando termine, verás un mensaje como este en la consola, indicando dónde se guardó tu transcripción:

```
Transcripción guardada en: output_transcripts/MiCancionFavorita_vid_dQw4w9WgXcQ_job_20231027123456789012.txt
```
El archivo `.txt` estará en la carpeta `output_transcripts`.

## 4. Opciones Adicionales (Opcional)

*   **Especificar Idioma**: Si Whisper no detecta bien el idioma, puedes ayudarlo:
    ```bash
    python yt_transcriber/cli.py --url "URL" --title "TITULO" --language es
    ```
    (Usa `es` para español, `en` para inglés, `fr` para francés, etc.)

## Configuración Avanzada (Opcional)

La aplicación usa configuraciones por defecto para el modelo de Whisper, carpetas temporales, etc. Si necesitas cambiarlas, puedes hacerlo editando el archivo `.env` (crea uno a partir de `.env.example`) o directamente en `yt_transcriber/config.py`.
