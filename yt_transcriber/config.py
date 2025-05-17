# Configuraciones para la aplicación de transcripción de YouTube
import os

from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env si existe
# Esto permite anular las configuraciones por defecto mediante un archivo .env local
# que no se sube al control de versiones.
load_dotenv()

# --- Configuración del Modelo Whisper ---
# Intenta leer desde variables de entorno, si no, usa el valor por defecto.
# Ejemplo en .env: WHISPER_MODEL_NAME="small"
WHISPER_MODEL_NAME = os.getenv(
    "WHISPER_MODEL_NAME", "base"
)  # Modelo por defecto, ej: "tiny", "base", "small", "medium", "large"

# Ejemplo en .env: WHISPER_DEVICE="cuda"
WHISPER_DEVICE = os.getenv(
    "WHISPER_DEVICE", "cpu"
)  # Dispositivo para Whisper, ej: "cpu", "cuda" si hay GPU


# --- Directorios ---
# Estos también pueden ser configurados vía .env si se desea flexibilidad en el despliegue.
# Ejemplo en .env: TEMP_DOWNLOAD_DIR="my_custom_temp/"
TEMP_DOWNLOAD_DIR = os.getenv(
    "TEMP_DOWNLOAD_DIR", "temp_files/"
)  # Directorio para archivos temporales (videos, audios)

# Ejemplo en .env: OUTPUT_TRANSCRIPTS_DIR="my_custom_output/"
OUTPUT_TRANSCRIPTS_DIR = os.getenv(
    "OUTPUT_TRANSCRIPTS_DIR", "output_transcripts/"
)  # Directorio para las transcripciones guardadas
