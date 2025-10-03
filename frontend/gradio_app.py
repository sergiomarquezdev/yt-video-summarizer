"""Gradio web interface for YouTube Video Transcriber & Script Generator.

This module provides a simple web UI with two main functionalities:
1. Transcribe YouTube videos to text
2. Generate AI-powered scripts from successful videos in your niche

Usage:
    uv run python frontend/gradio_app.py
    # Opens browser at http://localhost:7860
"""

import logging
from pathlib import Path

import gradio as gr

from yt_transcriber.cli import run_generate_script_command, run_transcribe_command
from yt_transcriber.config import settings


logger = logging.getLogger(__name__)


def transcribe_video_ui(
    url: str,
    language: str,
    ffmpeg_location: str,
) -> tuple[str, str | None]:
    """Transcribe a YouTube video via Gradio UI.

    Args:
        url: YouTube video URL
        language: Optional language code (e.g., 'es', 'en')
        ffmpeg_location: Optional custom FFmpeg path

    Returns:
        Tuple of (status_message, transcript_path)
    """
    try:
        # Validate inputs
        if not url or not url.strip():
            return "❌ Error: Debes proporcionar una URL de YouTube", None

        # Prepare arguments
        url = url.strip()
        lang = language.strip() if language and language.strip() else None
        ffmpeg = ffmpeg_location.strip() if ffmpeg_location and ffmpeg_location.strip() else None

        # Run transcription
        logger.info(f"Starting transcription for URL: {url}")
        transcript_path = run_transcribe_command(
            url=url,
            language=lang,
            ffmpeg_location=ffmpeg,
        )

        # Read transcript content for display
        if transcript_path and Path(transcript_path).exists():
            success_msg = f"✅ Transcripción completada!\n\n📄 Archivo: {transcript_path}\n\n"
            return success_msg, transcript_path
        else:
            return "❌ Error: La transcripción falló (archivo no generado)", None

    except Exception as e:
        logger.error(f"Transcription error in UI: {e}", exc_info=True)
        return f"❌ Error durante la transcripción: {str(e)}", None


def generate_script_ui(
    idea: str,
    max_videos: int,
    duration: int,
    style: str,
) -> tuple[str, str | None, str | None]:
    """Generate a YouTube script via Gradio UI.

    Args:
        idea: Video topic/idea
        max_videos: Maximum videos to analyze (5-20)
        duration: Target video duration in minutes (5-30)
        style: Video style (e.g., "casual", "educational")

    Returns:
        Tuple of (status_message, script_path_en, script_path_es)
    """
    try:
        # Validate inputs
        if not idea or not idea.strip():
            return "❌ Error: Debes proporcionar una idea para el video", None, None

        # Prepare arguments
        idea = idea.strip()
        video_style = style.strip() if style and style.strip() else None

        # Run script generation
        logger.info(f"Starting script generation for idea: {idea}")
        script_path_en, script_path_es = run_generate_script_command(
            idea=idea,
            max_videos=max_videos,
            duration=duration,
            style=video_style,
        )

        # Verify outputs
        en_exists = script_path_en and Path(script_path_en).exists()
        es_exists = script_path_es and Path(script_path_es).exists()

        if en_exists and es_exists:
            success_msg = (
                f"✅ ¡Guiones generados correctamente!\n\n"
                f"📄 Inglés: {script_path_en}\n"
                f"📄 Español: {script_path_es}\n\n"
                f"🎯 Videos analizados: {max_videos}\n"
                f"⏱️ Duración objetivo: {duration} minutos\n"
            )
            return success_msg, script_path_en, script_path_es
        else:
            return "❌ Error: La generación de guiones falló", None, None

    except Exception as e:
        logger.error(f"Script generation error in UI: {e}", exc_info=True)
        return f"❌ Error durante la generación: {str(e)}", None, None


# ============================================================================
# DARK THEME - One Daily Blog Color Palette
# ============================================================================
# Colors extracted from: https://github.com/sergiomarquezdev/one-daily-blog
# Dark mode palette for consistent branding

custom_theme = gr.themes.Base(
    primary_hue=gr.themes.Color(
        c50="#e0f2fe",
        c100="#b9e5ff",
        c200="#7dd3fc",
        c300="#38bdf8",
        c400="#22d3ee",  # Electric Cyan (accent)
        c500="#22d3ee",
        c600="#0891b2",
        c700="#0e7490",
        c800="#155e75",
        c900="#164e63",
        c950="#083344",
    ),
    secondary_hue=gr.themes.Color(
        c50="#f8fafc",
        c100="#f1f5f9",
        c200="#e2e8f0",
        c300="#cbd5e1",  # Light Gray (text)
        c400="#94a3b8",
        c500="#64748b",
        c600="#475569",
        c700="#334155",
        c800="#1e293b",  # Dark Slate (cards)
        c900="#0f172a",  # Rich Black (background)
        c950="#020617",
    ),
    neutral_hue=gr.themes.Color(
        c50="#f8fafc",
        c100="#f1f5f9",
        c200="#e2e8f0",
        c300="#cbd5e1",
        c400="#94a3b8",
        c500="#64748b",
        c600="#475569",
        c700="#334155",
        c800="#1e293b",
        c900="#0f172a",
        c950="#020617",
    ),
).set(
    body_background_fill="#0f172a",  # Rich Black
    body_text_color="#cbd5e1",  # Light Gray
    button_primary_background_fill="#22d3ee",  # Electric Cyan
    button_primary_background_fill_hover="#60a5fa",  # Sky Blue
    button_primary_text_color="#0f172a",  # Dark text on cyan
    block_background_fill="#1e293b",  # Dark Slate
    input_background_fill="#1e293b",  # Dark Slate
    border_color_primary="#617085",  # Lighter Gray border
)

# Minimal CSS - Only essential overrides
custom_css = """
/* Primary action buttons - Gradient effect */
button.primary {
    background: linear-gradient(135deg, #22d3ee 0%, #60a5fa 100%) !important;
    font-weight: 600;
}

button.primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 16px rgba(34, 211, 238, 0.3);
}

/* Spacing between columns */
.main-layout {
    gap: 2rem !important;
}
"""

# Build Gradio interface
with gr.Blocks(
    title="YouTube Tools - Transcriber & Script Generator",
    css=custom_css,
    theme=custom_theme,
) as app:
    # ===== MAIN HEADER =====
    gr.Markdown(
        """
        # 🎬 YouTube Tools - Transcriber & Script Generator
        Herramientas potenciadas con IA para crear contenido de YouTube profesional
        """
    )

    # ===== TWO-COLUMN LAYOUT =====
    with gr.Row(elem_classes="main-layout"):
        # ===== LEFT COLUMN: TRANSCRIBE VIDEO =====
        with gr.Column(scale=1):
            gr.Markdown("## 🎬 Transcribir Video")

            # Input Group
            with gr.Group():
                transcribe_url = gr.Textbox(
                    label="URL de YouTube",
                    placeholder="https://www.youtube.com/watch?v=VIDEO_ID",
                    lines=1,
                    info="Pega aquí la URL del video",
                )

                transcribe_language = gr.Dropdown(
                    label="Idioma",
                    choices=["Auto-detectar", "es", "en", "fr", "de", "it", "pt"],
                    value="Auto-detectar",
                    info="Detección automática recomendada",
                )

                transcribe_ffmpeg = gr.Textbox(
                    label="Ruta FFmpeg (opcional)",
                    placeholder="C:\\ffmpeg\\bin\\ffmpeg.exe",
                    lines=1,
                    info="Solo si no está en PATH",
                )

            transcribe_btn = gr.Button(
                "🚀 Transcribir Video",
                variant="primary",
                size="lg",
            )

            # Output Group
            gr.Markdown("### 📄 Resultado")
            transcribe_output = gr.Textbox(
                label="Transcripción",
                lines=6,
                interactive=False,
                show_copy_button=True,
            )

            transcribe_file = gr.File(
                label="Descargar archivo",
                interactive=False,
            )

        # ===== RIGHT COLUMN: GENERATE SCRIPT =====
        with gr.Column(scale=1):
            gr.Markdown("## 📝 Generar Guión")

            # Input Group
            with gr.Group():
                generate_idea = gr.Textbox(
                    label="Idea del Video",
                    placeholder="Tutorial de Python async para principiantes",
                    lines=2,
                    info="Describe el tema de tu video",
                )

                # Compact sliders side by side
                with gr.Row():
                    generate_max_videos = gr.Slider(
                        label="Videos a Analizar",
                        minimum=5,
                        maximum=20,
                        value=10,
                        step=1,
                    )

                    generate_duration = gr.Slider(
                        label="Duración (min)",
                        minimum=5,
                        maximum=30,
                        value=15,
                        step=1,
                    )

                generate_style = gr.Textbox(
                    label="Estilo (opcional)",
                    placeholder="casual, educativo, profesional...",
                    lines=1,
                    info="Tono y estilo del guión",
                )

            generate_btn = gr.Button(
                "🚀 Generar Guión",
                variant="primary",
                size="lg",
            )

            # Output Group
            gr.Markdown("### 📄 Resultados")
            generate_output = gr.Textbox(
                label="Guión generado",
                lines=6,
                interactive=False,
                show_copy_button=True,
            )

            # Bilingual downloads side by side
            with gr.Row():
                generate_file_en = gr.File(
                    label="📥 Inglés (EN)",
                    interactive=False,
                )

                generate_file_es = gr.File(
                    label="📥 Español (ES)",
                    interactive=False,
                )

    # ===== FOOTER CONFIG =====
    gr.Markdown(
        f"""
        ---
        **⚙️ Configuración:** Whisper `{settings.WHISPER_MODEL_NAME}` ({settings.WHISPER_DEVICE}) • Google Gemini API  
        **📁 Outputs:** `{settings.OUTPUT_TRANSCRIPTS_DIR}` • `{settings.SCRIPT_OUTPUT_DIR}`
        """,
    )

    # ===== EVENT HANDLERS =====

    # Transcribe button click
    transcribe_btn.click(
        fn=transcribe_video_ui,
        inputs=[
            transcribe_url,
            transcribe_language,
            transcribe_ffmpeg,
        ],
        outputs=[
            transcribe_output,
            transcribe_file,
        ],
        api_name="transcribe",
    )

    # Generate script button click
    generate_btn.click(
        fn=generate_script_ui,
        inputs=[
            generate_idea,
            generate_max_videos,
            generate_duration,
            generate_style,
        ],
        outputs=[
            generate_output,
            generate_file_en,
            generate_file_es,
        ],
        api_name="generate_script",
    )


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Launch Gradio app
    logger.info("Starting Gradio web interface...")
    app.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,  # Default Gradio port
        share=False,  # Set to True to create public URL
        show_error=True,  # Show detailed errors in UI
        inbrowser=True,  # Auto-open browser
    )
