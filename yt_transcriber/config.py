# Configuraciones para la aplicación de transcripción de YouTube

import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Cargar variables de entorno desde un archivo .env si existe
load_dotenv()


class AppSettings(BaseSettings):
    """
    Configuraciones de la aplicación, validadas con Pydantic.
    Lee variables de entorno y aplica valores por defecto.
    """

    model_config = SettingsConfigDict(case_sensitive=False)

    WHISPER_MODEL_NAME: Literal["tiny", "base", "small", "medium", "large"] = Field(
        default="base",
        description="Modelo de Whisper a utilizar",
    )
    WHISPER_DEVICE: Literal["cpu", "cuda"] = Field(
        default="cpu",
        description="Dispositivo para ejecutar Whisper (cpu o cuda)",
    )
    TEMP_DOWNLOAD_DIR: Path = Field(
        default=Path("temp_files/"),
        description="Directorio para archivos temporales",
    )
    OUTPUT_TRANSCRIPTS_DIR: Path = Field(
        default=Path("output_transcripts/"),
        description="Directorio para transcripciones generadas",
    )
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Nivel de logging",
    )
    FFMPEG_LOCATION: str = Field(
        default="",
        description="Ruta personalizada a FFmpeg (opcional)",
    )


# Crear una instancia global de las configuraciones validadas
try:
    settings = AppSettings()
except Exception as e:
    sys.stderr.write(f"CRITICAL: Error al cargar o validar la configuración: {e}\n")
    sys.exit(1)
