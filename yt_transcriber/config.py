# Configuraciones para la aplicación de transcripción de YouTube
# mypy: disable-error-code="call-overload,call-arg"
# Note: Pydantic Settings causes mypy false positives with Field() env parameter
# and BaseSettings() initialization. These are safe to ignore.

import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


# Cargar variables de entorno desde un archivo .env si existe
load_dotenv()


class AppSettings(BaseSettings):
    """
    Configuraciones de la aplicación, validadas con Pydantic.
    Lee variables de entorno y aplica valores por defecto.
    """

    WHISPER_MODEL_NAME: Literal["tiny", "base", "small", "medium", "large"] = Field(
        "base", env="WHISPER_MODEL_NAME"
    )
    WHISPER_DEVICE: Literal["cpu", "cuda"] = Field("cpu", env="WHISPER_DEVICE")
    TEMP_DOWNLOAD_DIR: Path = Field("temp_files/", env="TEMP_DOWNLOAD_DIR")
    OUTPUT_TRANSCRIPTS_DIR: Path = Field("output_transcripts/", env="OUTPUT_TRANSCRIPTS_DIR")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        "INFO", env="LOG_LEVEL"
    )
    FFMPEG_LOCATION: str = Field("", env="FFMPEG_LOCATION")

    class Config:
        # Pydantic v1 style for case-insensitivity
        case_sensitive = False
        # For Pydantic v2, you would use:
        # validation_options = {"case_sensitive": False}


# Crear una instancia global de las configuraciones validadas
try:
    settings = AppSettings()
except Exception as e:
    sys.stderr.write(f"CRITICAL: Error al cargar o validar la configuración: {e}\n")
    sys.exit(1)
