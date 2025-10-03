import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

from yt_transcriber import config, downloader, transcriber, utils
from yt_transcriber.downloader import DownloadError
from yt_transcriber.transcriber import TranscriptionError


# Initialize Rich console for beautiful output
console = Console()


# Configuración del logger
logger = logging.getLogger(__name__)


def setup_logging():
    """Configura el logging básico para la aplicación."""
    logging.basicConfig(
        level=config.settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def load_whisper_model():
    """Carga y devuelve el modelo Whisper según la configuración."""
    logger.info("Cargando modelo Whisper...")
    try:
        import torch
        import whisper
    except ImportError as e:
        logger.critical(
            f"Dependencias críticas no encontradas. Asegúrate de que torch y whisper estén instalados. Error: {e}"
        )
        sys.exit(1)

    device = config.settings.WHISPER_DEVICE
    if device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA no disponible. Cambiando a CPU para Whisper.")
        device = "cpu"

    try:
        model = whisper.load_model(config.settings.WHISPER_MODEL_NAME, device=device)
        logger.info(f"Modelo Whisper '{config.settings.WHISPER_MODEL_NAME}' cargado en '{device}'.")
        return model
    except Exception as e:
        logger.critical(
            f"Fallo CRÍTICO al cargar modelo Whisper en '{device}'. Error: {e}",
            exc_info=True,
        )
        sys.exit(1)


def get_youtube_title(youtube_url: str) -> str:
    """Extrae el título de un video de YouTube usando yt-dlp."""
    try:
        import yt_dlp

        with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if info is None:
                return "untitled"
            title: str = info.get("title", "untitled")  # type: ignore[assignment]
            return title
    except Exception as e:
        logger.error(f"No se pudo extraer el título automáticamente: {e}")
        return "untitled"


def process_transcription(
    youtube_url: str,
    title: str,
    model,
    language: str | None = None,
    ffmpeg_location: str | None = None,
) -> Path | None:
    """
    Lógica principal para descargar, transcribir y guardar la transcripción.
    """
    logger.info(f"Iniciando transcripción para URL: {youtube_url}")
    unique_job_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    job_temp_dir = config.settings.TEMP_DOWNLOAD_DIR / unique_job_id

    try:
        # 1. Descargar video y extraer audio
        logger.info("Paso 1: Descargando y extrayendo audio...")
        download_result = downloader.download_and_extract_audio(
            youtube_url=youtube_url,
            temp_dir=job_temp_dir,
            unique_job_id=unique_job_id,
            ffmpeg_location=ffmpeg_location,
        )
        logger.info(f"Audio extraído a: {download_result.audio_path}")

        # 2. Transcribir el audio
        logger.info("Paso 2: Transcribiendo audio...")
        transcription_result = transcriber.transcribe_audio_file(
            audio_path=download_result.audio_path, model=model, language=language
        )
        logger.info(f"Transcripción completada. Idioma detectado: {transcription_result.language}")

        # 3. Guardar la transcripción
        logger.info("Paso 3: Guardando transcripción...")
        normalized_title = utils.normalize_title_for_filename(title)
        output_filename_base = (
            f"{normalized_title}_vid_{download_result.video_id}_job_{unique_job_id}"
        )
        output_file_path = utils.save_transcription_to_file(
            transcription_text=transcription_result.text,
            output_filename_no_ext=output_filename_base,
            output_dir=config.settings.OUTPUT_TRANSCRIPTS_DIR,
            original_title=title,
        )

        if not output_file_path:
            raise OSError("No se pudo guardar el archivo de transcripción.")

        logger.info(f"Transcripción guardada exitosamente en: {output_file_path}")
        print(f"\nTranscripción guardada en: {output_file_path}")
        return output_file_path

    except (OSError, DownloadError, TranscriptionError) as e:
        logger.error(f"Ha ocurrido un error en el proceso: {e}", exc_info=True)
        print(f"\nError: {e}", file=sys.stderr)
        return None
    except Exception as e:
        logger.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
        print(f"\nError inesperado: {e}", file=sys.stderr)
        return None
    finally:
        # 4. Limpieza
        logger.info(f"Limpiando directorio temporal: {job_temp_dir}")
        utils.cleanup_temp_dir(job_temp_dir)


def command_transcribe(args):
    """Command handler for transcribing a single YouTube video."""
    setup_logging()

    # Validar la URL de YouTube
    if not (
        args.url.startswith("https://www.youtube.com/") or args.url.startswith("https://youtu.be/")
    ):
        logger.error(f"URL de YouTube no válida: {args.url}")
        print("Error: La URL no parece ser una URL válida de YouTube.", file=sys.stderr)
        sys.exit(1)

    # Cargar el modelo Whisper
    model = load_whisper_model()

    # Obtener título y procesar
    logger.info("Extrayendo título del video...")
    title = get_youtube_title(args.url)
    logger.info(f"Título extraído: {title}")

    result_path = process_transcription(
        youtube_url=args.url,
        title=title,
        model=model,
        language=args.language,
        ffmpeg_location=args.ffmpeg_location,
    )

    if result_path:
        logger.info("Proceso completado exitosamente.")
        sys.exit(0)
    else:
        logger.error("El proceso de transcripción falló.")
        sys.exit(1)


def command_generate_script(args):
    """Command handler for generating YouTube scripts from search."""
    from time import time

    from youtube_script_generator import (
        BatchProcessor,
        PatternAnalyzer,
        PatternSynthesizer,
        QueryOptimizer,
        ScriptGenerator,
        YouTubeSearcher,
    )

    setup_logging()

    start_time = time()

    # Display header
    console.print("\n[bold cyan]🎬 YouTube-Powered Script Generator[/bold cyan]")
    console.print("━" * 50)
    console.print(f"\n[bold]💡 Idea:[/bold] {args.idea}")
    console.print()

    try:
        # Phase 1: Query Optimization
        console.print("[bold yellow]🔧 Optimizando query de búsqueda...[/bold yellow]")
        optimizer = QueryOptimizer()
        optimized = optimizer.optimize(args.idea)
        console.print(
            f"   [green]✓[/green] Query optimizada: [cyan]{optimized.optimized_query}[/cyan]"
        )
        console.print()

        # Phase 2: YouTube Search
        console.print("[bold yellow]🔍 Buscando videos en YouTube...[/bold yellow]")
        searcher = YouTubeSearcher(max_results=args.max_videos)
        videos = searcher.search(
            optimized.optimized_query,
            min_duration=args.min_duration,
            max_duration=args.max_duration,
        )
        avg_duration = sum(v.duration_minutes for v in videos) / len(videos)
        avg_views = sum(v.view_count for v in videos) / len(videos)
        console.print(
            f"   [green]✓[/green] {len(videos)} videos encontrados "
            f"(duración prom: {avg_duration:.1f} min, views prom: {avg_views / 1000:.1f}K)"
        )
        console.print()

        # Phase 3: Batch Processing (Download + Transcribe)
        console.print(
            f"[bold yellow]📥 Descargando y transcribiendo {len(videos)} videos...[/bold yellow]"
        )
        processor = BatchProcessor()
        transcripts = processor.process_videos(videos)
        console.print(f"   [green]✓[/green] {len(transcripts)} videos procesados exitosamente")
        console.print()

        # Phase 4: Pattern Analysis
        console.print(
            f"[bold yellow]📊 Analizando patrones de {len(transcripts)} videos...[/bold yellow]"
        )
        analyzer = PatternAnalyzer()
        analyses = [analyzer.analyze(t) for t in transcripts]
        avg_effectiveness = sum(a.effectiveness_score for a in analyses) / len(analyses)
        console.print(
            f"   [green]✓[/green] Análisis completado "
            f"(efectividad promedio: {avg_effectiveness:.1f}/5.0)"
        )
        console.print()

        # Phase 5: Pattern Synthesis
        console.print("[bold yellow]🧠 Sintetizando mejores prácticas...[/bold yellow]")
        synthesizer = PatternSynthesizer()
        synthesis = synthesizer.synthesize(analyses, topic=args.idea)
        console.print(
            f"   [green]✓[/green] Síntesis completada "
            f"({len(synthesis.top_hooks)} hooks, "
            f"{len(synthesis.effective_ctas)} CTAs, "
            f"{len(synthesis.notable_techniques)} técnicas)"
        )
        console.print()

        # Phase 6: Script Generation
        console.print("[bold yellow]✍️ Generando guión optimizado...[/bold yellow]")
        generator = ScriptGenerator()
        script = generator.generate(
            synthesis=synthesis,
            user_idea=args.idea,
            duration_minutes=args.duration,
            style_preference=args.style,
        )
        console.print(
            f"   [green]✓[/green] Guión generado "
            f"({script.word_count} palabras, {script.estimated_duration_minutes} min)"
        )
        console.print()

        # Phase 7: Translation to Spanish
        console.print("[bold yellow]🌍 Traduciendo guión al español...[/bold yellow]")
        from youtube_script_generator.translator import ScriptTranslator

        translator = ScriptTranslator()
        script_es = translator.translate_to_spanish(script)
        console.print(
            f"   [green]✓[/green] Traducción completada "
            f"({script_es.word_count} palabras en español)"
        )
        console.print()

        # Save outputs
        console.print("[bold yellow]💾 Guardando archivos...[/bold yellow]")

        # Ensure output directories exist
        output_scripts = Path("output_scripts")
        output_analysis = Path("output_analysis")
        output_scripts.mkdir(exist_ok=True)
        output_analysis.mkdir(exist_ok=True)

        # Generate safe filename from idea
        safe_filename = "".join(c if c.isalnum() or c in " -_" else "_" for c in args.idea)
        safe_filename = safe_filename.replace(" ", "_")[:50]

        # Save English script
        script_path_en = output_scripts / f"{safe_filename}_EN.md"
        script_path_en.write_text(script.script_markdown, encoding="utf-8")

        # Save Spanish script
        script_path_es = output_scripts / f"{safe_filename}_ES.md"
        script_path_es.write_text(script_es.script_markdown, encoding="utf-8")

        # Save synthesis report
        synthesis_path = output_analysis / f"{safe_filename}_synthesis.md"
        synthesis_path.write_text(synthesis.markdown_report, encoding="utf-8")

        console.print(f"   [green]✓[/green] Guión (EN) guardado: [cyan]{script_path_en}[/cyan]")
        console.print(f"   [green]✓[/green] Guión (ES) guardado: [cyan]{script_path_es}[/cyan]")
        console.print(f"   [green]✓[/green] Síntesis guardada: [cyan]{synthesis_path}[/cyan]")
        console.print()

        # Display summary
        elapsed = time() - start_time
        console.print("━" * 50)
        console.print(
            f"[bold green]✅ Proceso completado en {elapsed / 60:.0f}m {elapsed % 60:.0f}s[/bold green]"
        )
        console.print()

        console.print("[bold]📄 Estadísticas del guión:[/bold]")
        console.print(f"   - Título: {script.seo_title}")
        console.print(f"   - Duración estimada: {script.estimated_duration_minutes} minutos")
        console.print(f"   - Palabras: {script.word_count:,}")
        console.print(f"   - Tags SEO: {len(script.seo_tags)}")
        console.print(f"   - Calidad estimada: {script.estimated_quality_score}/100")
        console.print()

        console.print(
            f"[bold]🎯 Basado en análisis de {synthesis.num_videos_analyzed} videos "
            f"(efectividad prom: {synthesis.average_effectiveness:.1f}/5.0)[/bold]"
        )
        console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Proceso interrumpido por el usuario[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error durante la generación: {e}", exc_info=True)
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        sys.exit(1)


def run_transcribe_command(
    url: str,
    language: str | None = None,
    ffmpeg_location: str | None = None,
) -> str | None:
    """Wrapper function for transcription to be called from Gradio UI.

    Args:
        url: YouTube video URL
        language: Optional language code (e.g., 'es', 'en')
        ffmpeg_location: Optional custom FFmpeg path

    Returns:
        Path to the saved transcript file, or None if failed
    """
    setup_logging()

    # Validate YouTube URL
    if not (url.startswith("https://www.youtube.com/") or url.startswith("https://youtu.be/")):
        logger.error(f"Invalid YouTube URL: {url}")
        return None

    # Load Whisper model
    model = load_whisper_model()

    # Get title and process
    logger.info("Extracting video title...")
    title = get_youtube_title(url)
    logger.info(f"Title extracted: {title}")

    # Handle "Auto-detectar" option from Gradio dropdown
    lang = None if language == "Auto-detectar" else language

    result_path = process_transcription(
        youtube_url=url,
        title=title,
        model=model,
        language=lang,
        ffmpeg_location=ffmpeg_location,
    )

    if result_path:
        return str(result_path)
    else:
        return None


def run_generate_script_command(
    idea: str,
    max_videos: int = 10,
    duration: int = 10,
    style: str | None = None,
) -> tuple[str | None, str | None]:
    """Wrapper function for script generation to be called from Gradio UI.

    Args:
        idea: Video topic/idea
        max_videos: Maximum videos to analyze (5-20)
        duration: Target video duration in minutes (5-30)
        style: Optional video style (e.g., "casual", "educational")

    Returns:
        Tuple of (script_path_en, script_path_es) or (None, None) if failed
    """
    from time import time

    from youtube_script_generator import (
        BatchProcessor,
        PatternAnalyzer,
        PatternSynthesizer,
        QueryOptimizer,
        ScriptGenerator,
        YouTubeSearcher,
    )
    from youtube_script_generator.translator import ScriptTranslator

    setup_logging()

    start_time = time()

    try:
        # Phase 1: Query Optimization
        logger.info("Phase 1: Optimizing search query...")
        optimizer = QueryOptimizer()
        optimized = optimizer.optimize(idea)

        # Phase 2: YouTube Search
        logger.info("Phase 2: Searching YouTube videos...")
        searcher = YouTubeSearcher(max_results=max_videos)
        videos = searcher.search(
            optimized.optimized_query,
            min_duration=5,  # Fixed range for now
            max_duration=45,
        )

        # Phase 3: Batch Processing
        logger.info(f"Phase 3: Processing {len(videos)} videos...")
        processor = BatchProcessor()
        transcripts = processor.process_videos(videos)

        # Phase 4: Pattern Analysis
        logger.info(f"Phase 4: Analyzing patterns from {len(transcripts)} videos...")
        analyzer = PatternAnalyzer()
        analyses = [analyzer.analyze(t) for t in transcripts]

        # Phase 5: Pattern Synthesis
        logger.info("Phase 5: Synthesizing best practices...")
        synthesizer = PatternSynthesizer()
        synthesis = synthesizer.synthesize(analyses, topic=idea)

        # Phase 6: Script Generation
        logger.info("Phase 6: Generating optimized script...")
        generator = ScriptGenerator()
        script = generator.generate(
            synthesis=synthesis,
            user_idea=idea,
            duration_minutes=duration,
            style_preference=style,
        )

        # Phase 7: Translation to Spanish
        logger.info("Phase 7: Translating script to Spanish...")
        translator = ScriptTranslator()
        script_es = translator.translate_to_spanish(script)

        # Save outputs
        logger.info("Saving output files...")
        output_scripts = Path("output_scripts")
        output_analysis = Path("output_analysis")
        output_scripts.mkdir(exist_ok=True)
        output_analysis.mkdir(exist_ok=True)

        # Generate safe filename
        safe_filename = "".join(c if c.isalnum() or c in " -_" else "_" for c in idea)
        safe_filename = safe_filename.replace(" ", "_")[:50]

        # Save scripts
        script_path_en = output_scripts / f"{safe_filename}_EN.md"
        script_path_en.write_text(script.script_markdown, encoding="utf-8")

        script_path_es = output_scripts / f"{safe_filename}_ES.md"
        script_path_es.write_text(script_es.script_markdown, encoding="utf-8")

        # Save synthesis report
        synthesis_path = output_analysis / f"{safe_filename}_synthesis.md"
        synthesis_path.write_text(synthesis.markdown_report, encoding="utf-8")

        elapsed = time() - start_time
        logger.info(f"Process completed in {elapsed / 60:.0f}m {elapsed % 60:.0f}s")

        return str(script_path_en), str(script_path_es)

    except Exception as e:
        logger.error(f"Error during script generation: {e}", exc_info=True)
        return None, None


def main():
    """Punto de entrada principal para el CLI."""
    parser = argparse.ArgumentParser(
        description="YouTube Video Transcriber & Script Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Subcommand: transcribe
    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="Transcribe un video de YouTube a texto",
    )
    transcribe_parser.add_argument(
        "-u",
        "--url",
        required=True,
        type=str,
        help="URL completa del video de YouTube.",
    )
    transcribe_parser.add_argument(
        "-l",
        "--language",
        type=str,
        default=None,
        help="Código de idioma (ej. 'en', 'es') para forzar la transcripción en ese idioma.",
    )
    transcribe_parser.add_argument(
        "--ffmpeg-location",
        type=str,
        default=None,
        help="Ruta personalizada a FFmpeg (ej. 'C:\\ffmpeg\\bin\\ffmpeg.exe').",
    )

    # Subcommand: generate-script
    generate_parser = subparsers.add_parser(
        "generate-script",
        help="Genera un guión de YouTube basado en videos exitosos",
    )
    generate_parser.add_argument(
        "-i",
        "--idea",
        required=True,
        type=str,
        help="Idea del video (ej. 'crear API REST con FastAPI')",
    )
    generate_parser.add_argument(
        "-m",
        "--max-videos",
        type=int,
        default=10,
        help="Número máximo de videos a analizar (default: 10)",
    )
    generate_parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=10,
        help="Duración objetivo del guión en minutos (default: 10)",
    )
    generate_parser.add_argument(
        "--min-duration",
        type=int,
        default=5,
        help="Duración mínima de videos a buscar en minutos (default: 5)",
    )
    generate_parser.add_argument(
        "--max-duration",
        type=int,
        default=45,
        help="Duración máxima de videos a buscar en minutos (default: 45)",
    )
    generate_parser.add_argument(
        "-s",
        "--style",
        type=str,
        default=None,
        help="Preferencia de estilo (ej. 'educational', 'entertaining')",
    )

    args = parser.parse_args()

    # Handle subcommands
    if args.command == "transcribe":
        command_transcribe(args)
    elif args.command == "generate-script":
        command_generate_script(args)
    else:
        parser.print_help()
        sys.exit(1)
        sys.exit(1)


if __name__ == "__main__":
    main()
