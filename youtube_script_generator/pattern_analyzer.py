"""Pattern Analyzer - Extracts patterns from video transcripts using Gemini."""

import json
import logging

import google.generativeai as genai

from youtube_script_generator.models import VideoAnalysis, VideoTranscript
from yt_transcriber.config import settings


logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes video transcripts to extract patterns."""

    def __init__(self, model_name: str | None = None):
        """Initialize the pattern analyzer.

        Args:
            model_name: Gemini model name (defaults to config setting)
        """
        self.model_name = model_name or settings.GEMINI_PRO_MODEL
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.model_name)

    def analyze(self, transcript: VideoTranscript) -> VideoAnalysis:
        """Analyze a video transcript to extract patterns.

        Args:
            transcript: VideoTranscript to analyze

        Returns:
            VideoAnalysis with extracted patterns

        Raises:
            Exception: If analysis fails
        """
        logger.info(f"Analyzing transcript for: {transcript.video.title}")

        try:
            # Create structured prompt
            prompt = self._create_analysis_prompt(transcript)

            # Call Gemini API
            response = self.model.generate_content(prompt)

            # Parse JSON response
            analysis = self._parse_analysis_response(response.text, transcript)

            logger.info(f"Analysis complete for: {transcript.video.title}")
            return analysis

        except Exception as e:
            logger.error(f"Analysis failed for {transcript.video.title}: {e}")
            # Return empty analysis as fallback
            return VideoAnalysis(
                video=transcript.video,
                hook_start=0,
                hook_end=30,
                hook_text="",
                hook_type="unknown",
                hook_effectiveness="unknown",
                intro_end=30,
                sections=[],
                conclusion_start=transcript.video.duration_seconds - 60,
                ctas=[],
                technical_terms=[],
                common_phrases=[],
                transition_phrases=[],
                techniques=[],
                title_keywords=[],
                estimated_tags=[],
                raw_analysis="",
            )

    def _create_analysis_prompt(self, transcript: VideoTranscript) -> str:
        """Create a structured prompt for pattern analysis.

        Args:
            transcript: VideoTranscript to analyze

        Returns:
            Prompt string for Gemini
        """
        # Truncate very long transcripts to avoid token limits
        max_transcript_length = 15000
        transcript_text = transcript.transcript_text
        if len(transcript_text) > max_transcript_length:
            transcript_text = transcript_text[:max_transcript_length] + "... [truncated]"

        return f"""Analiza este transcript de un video de YouTube exitoso y extrae los patrones clave de su estructura y presentación.

**VIDEO**: {transcript.video.title}
**CANAL**: {transcript.video.channel}
**VIEWS**: {transcript.video.view_count:,}
**DURACIÓN**: {transcript.video.duration_minutes:.1f} minutos

**TRANSCRIPT**:
{transcript_text}

**TAREA**: Extrae los siguientes patrones del video:

1. **Opening Hook** (primeros 10-30 segundos): ¿Cómo captura la atención? Cita textual si es posible.

2. **CTAs** (Calls to Action): Lista todos los CTAs que aparecen (suscribirse, like, comentar, links, etc.) con el momento aproximado.

3. **Estructura del Video** (Secciones): Divide el contenido en secciones principales con timestamps aproximados y títulos.

4. **Patrones de Vocabulario**: Frases o expresiones que se repiten, lenguaje característico del creador.

5. **Términos Técnicos**: Conceptos clave o jerga específica del tema.

6. **Técnicas de Persuasión**: Storytelling, ejemplos, analogías, preguntas retóricas, etc.

7. **Pacing**: Ritmo del video (rápido, pausado, dinámico), cambios de ritmo.

8. **SEO Keywords**: Palabras clave principales del contenido (para búsqueda).

**FORMATO DE RESPUESTA**: JSON válido sin markdown. Ejemplo:

{{
    "opening_hook": "¿Sabías que Python puede hacer esto en una sola línea? Vamos a verlo.",
    "ctas": [
        {{"type": "like", "timestamp": "0:10", "text": "Dale like si quieres más tutoriales"}},
        {{"type": "subscribe", "timestamp": "5:30", "text": "Suscríbete para no perderte nada"}}
    ],
    "sections": [
        {{"title": "Introducción", "start": "0:00", "end": "1:00"}},
        {{"title": "Concepto Principal", "start": "1:00", "end": "3:30"}}
    ],
    "vocabulary_patterns": ["como puedes ver", "básicamente", "en este caso"],
    "technical_terms": ["list comprehension", "lambda functions", "generators"],
    "persuasion_techniques": ["Uso de preguntas para engagement", "Ejemplos del mundo real", "Demostración en vivo"],
    "pacing_notes": "Ritmo rápido en intro, más pausado en explicaciones técnicas, cierre dinámico",
    "seo_keywords": ["Python", "tutorial", "programación", "tips", "código"]
}}

Analiza el video ahora:"""

    def _parse_analysis_response(
        self,
        response_text: str,
        transcript: VideoTranscript,
    ) -> VideoAnalysis:
        """Parse Gemini's JSON response into VideoAnalysis.

        Args:
            response_text: Raw response from Gemini
            transcript: Original transcript

        Returns:
            VideoAnalysis object
        """
        try:
            # Remove markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            # Parse JSON
            data = json.loads(clean_text)

            # Extract hook information
            hook = data.get("opening_hook", "")
            sections = data.get("sections", [])

            # Determine hook start/end from sections or use defaults
            hook_start = 0
            hook_end = 30  # Default: first 30 seconds
            if sections and len(sections) > 0:
                first_section = sections[0]
                # Use the end of first section as hook end (typically "Introduction" section)
                if "end" in first_section:
                    # Parse timestamp like "0:30" to seconds
                    end_str = first_section["end"]
                    if ":" in end_str:
                        parts = end_str.split(":")
                        hook_end = int(parts[0]) * 60 + int(parts[1])
                    elif end_str.isdigit():
                        hook_end = int(end_str)

            return VideoAnalysis(
                video=transcript.video,
                # Hook
                hook_start=hook_start,
                hook_end=hook_end,
                hook_text=hook,
                hook_type=data.get("hook_type", "unknown"),
                hook_effectiveness=data.get("hook_effectiveness", "unknown"),
                intro_end=hook_end,
                # Structure
                sections=sections,
                conclusion_start=transcript.video.duration_seconds - 60,  # Last minute
                # CTAs
                ctas=data.get("ctas", []),
                # Vocabulary
                technical_terms=data.get("technical_terms", []),
                common_phrases=data.get("vocabulary_patterns", []),
                transition_phrases=data.get("transition_phrases", []),
                # Techniques
                techniques=[
                    {"name": t, "description": ""} for t in data.get("persuasion_techniques", [])
                ],
                # SEO
                title_keywords=data.get("seo_keywords", []),
                estimated_tags=data.get("seo_keywords", [])[:10],
                # Raw
                raw_analysis=response_text,
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(
                f"Failed to parse analysis response: {e}. Response: {response_text[:200]}"
            )
            # Return minimal analysis
            return VideoAnalysis(
                video=transcript.video,
                hook_start=0,
                hook_end=30,
                hook_text="",
                hook_type="unknown",
                hook_effectiveness="unknown",
                intro_end=30,
                sections=[],
                conclusion_start=transcript.video.duration_seconds - 60,
                ctas=[],
                technical_terms=[],
                common_phrases=[],
                transition_phrases=[],
                techniques=[],
                title_keywords=[],
                estimated_tags=[],
                raw_analysis=response_text,
            )
