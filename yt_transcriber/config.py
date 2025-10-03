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

    # YouTube Script Generator settings
    GOOGLE_API_KEY: str = Field(
        default="",
        description="Google Gemini API key para script generation",
    )

    # ========== GEMINI MODEL CONFIGURATION (Optimized for Quality + Cost) ==========

    # For script synthesis and generation (CRITICAL - needs max quality)
    GEMINI_PRO_MODEL: str = Field(
        default="gemini-2.5-pro",
        description="Modelo premium para synthesis y script generation ($2.50/$15.00)",
    )

    # For video summarization (balanced quality, free tier)
    SUMMARIZER_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Modelo para resúmenes de video (free tier, excelente calidad)",
    )

    # For pattern analysis from transcripts (10 videos, free tier)
    PATTERN_ANALYZER_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Modelo para análisis de patrones (free tier, suficiente calidad)",
    )

    # For translations (summaries use lite, scripts use flash)
    TRANSLATOR_MODEL: str = Field(
        default="gemini-2.5-flash-lite",
        description="Modelo para traducciones simples ($0.075/$0.30)",
    )

    # For simple tasks (query optimization)
    QUERY_OPTIMIZER_MODEL: str = Field(
        default="gemini-2.5-flash-lite",
        description="Modelo para optimización de queries ($0.075/$0.30)",
    )

    # ========== DIRECTORY CONFIGURATION ==========

    SCRIPT_OUTPUT_DIR: Path = Field(
        default=Path("output_scripts/"),
        description="Directorio para guiones generados",
    )
    ANALYSIS_OUTPUT_DIR: Path = Field(
        default=Path("output_analysis/"),
        description="Directorio para análisis y síntesis",
    )
    TEMP_BATCH_DIR: Path = Field(
        default=Path("temp_batch/"),
        description="Directorio temporal para batch processing",
    )
    SUMMARY_OUTPUT_DIR: Path = Field(
        default=Path("output_summaries/"),
        description="Directorio para resúmenes generados",
    )


# Crear una instancia global de las configuraciones validadas
try:
    settings = AppSettings()
except Exception as e:
    sys.stderr.write(f"CRITICAL: Error al cargar o validar la configuración: {e}\n")
    sys.exit(1)
