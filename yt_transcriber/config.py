# Configuraciones para la aplicación de transcripción de YouTube
import os
import sys  # Importar sys para el manejo de excepciones en la carga
from typing import Any, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, validator

# Cargar variables de entorno desde un archivo .env si existe
# Esto permite anular las configuraciones por defecto mediante un archivo .env local
# que no se sube al control de versiones.
load_dotenv()


class AppSettings(BaseModel):
    # Definir defaults aquí. Los validadores los pueden sobreescribir desde el entorno.
    WHISPER_MODEL_NAME: Literal["tiny", "base", "small", "medium", "large"] = "medium"
    WHISPER_DEVICE: Literal["cpu", "cuda"] = "cuda"
    TEMP_DOWNLOAD_DIR: str = "temp_files/"
    OUTPUT_TRANSCRIPTS_DIR: str = "output_transcripts/"
    LOG_LEVEL: str = "INFO"

    @validator("WHISPER_MODEL_NAME", pre=True, always=True)
    def _env_whisper_model_name(cls, v: Any) -> Any:
        env_val = os.getenv("WHISPER_MODEL_NAME")
        return env_val if env_val is not None else v

    @validator("WHISPER_DEVICE", pre=True, always=True)
    def _env_whisper_device(cls, v: Any) -> Any:
        env_val = os.getenv("WHISPER_DEVICE")
        val_to_check = env_val if env_val is not None else v
        if val_to_check not in ("cpu", "cuda"):
            raise ValueError(
                f"WHISPER_DEVICE debe ser 'cpu' o 'cuda', se obtuvo '{val_to_check}'"
            )
        return val_to_check

    @validator("TEMP_DOWNLOAD_DIR", pre=True, always=True)
    def _env_temp_download_dir(cls, v: Any) -> Any:
        env_val = os.getenv("TEMP_DOWNLOAD_DIR")
        return env_val if env_val is not None else v

    @validator("OUTPUT_TRANSCRIPTS_DIR", pre=True, always=True)
    def _env_output_transcripts_dir(cls, v: Any) -> Any:
        env_val = os.getenv("OUTPUT_TRANSCRIPTS_DIR")
        return env_val if env_val is not None else v

    @validator("LOG_LEVEL", pre=True, always=True)
    def _env_log_level(cls, v: Any) -> Any:
        env_val = os.getenv("LOG_LEVEL")
        val_to_check = env_val if env_val is not None else v

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        processed_val = str(val_to_check).upper()

        if processed_val not in valid_log_levels:
            raise ValueError(
                f"LOG_LEVEL debe ser uno de {valid_log_levels}, se obtuvo '{val_to_check}'"
            )
        return processed_val


# Crear una instancia global de las configuraciones validadas
try:
    # Ahora AppSettings() usará los defaults de la clase, y los validadores
    # intentarán sobreescribirlos con variables de entorno si existen.
    settings = AppSettings()
except Exception as e:  # Captura más genérica por si Pydantic u otra cosa falla
    # Usar sys.stderr.write y sys.exit para errores críticos al inicio
    sys.stderr.write(f"CRITICAL: Error al cargar o validar la configuración: {e}\n")
    sys.exit(1)  # Salir si la configuración es inválida

# Exportar variables individuales para importación directa si se prefiere,
# aunque settings.VARIABLE es el método recomendado.
WHISPER_MODEL_NAME = settings.WHISPER_MODEL_NAME
WHISPER_DEVICE = settings.WHISPER_DEVICE
TEMP_DOWNLOAD_DIR = settings.TEMP_DOWNLOAD_DIR
OUTPUT_TRANSCRIPTS_DIR = settings.OUTPUT_TRANSCRIPTS_DIR
LOG_LEVEL = settings.LOG_LEVEL
