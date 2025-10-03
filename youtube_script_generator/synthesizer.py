"""Synthesizer - Combines multiple video analyses into patterns using Gemini."""

import json
import logging
from collections import Counter
from datetime import UTC, datetime

import google.generativeai as genai

from youtube_script_generator.models import PatternSynthesis, VideoAnalysis
from yt_transcriber.config import settings


logger = logging.getLogger(__name__)


class PatternSynthesizer:
    """Synthesizes patterns from multiple video analyses.

    This class takes multiple VideoAnalysis objects and creates a comprehensive
    synthesis that identifies the most common and effective patterns across
    all analyzed videos.

    Features:
    - Weighted by video quality scores (higher quality = more influence)
    - Top N extraction for each pattern category
    - Frequency analysis for common patterns
    - Structured synthesis report generation
    """

    def __init__(self, model_name: str | None = None):
        """Initialize the pattern synthesizer.

        Args:
            model_name: Gemini model name (defaults to config setting)
        """
        self.model_name = model_name or settings.GEMINI_PRO_MODEL
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.model_name)

    def synthesize(
        self,
        analyses: list[VideoAnalysis],
        topic: str = "YouTube Script Patterns",
    ) -> PatternSynthesis:
        """Synthesize patterns from multiple video analyses.

        Args:
            analyses: List of VideoAnalysis objects to synthesize
            topic: Topic/theme of the videos (for context)

        Returns:
            PatternSynthesis object with aggregated patterns

        Raises:
            ValueError: If analyses list is empty
        """
        if not analyses:
            raise ValueError("Cannot synthesize from empty analyses list")

        logger.info(f"Synthesizing patterns from {len(analyses)} videos for topic: {topic}")

        # Extract weighted patterns
        top_hooks = self._extract_top_hooks(analyses, top_n=10)
        optimal_structure = self._calculate_optimal_structure(analyses)
        effective_ctas = self._extract_effective_ctas(analyses, top_n=15)
        key_vocabulary = self._aggregate_vocabulary(analyses)
        notable_techniques = self._extract_notable_techniques(analyses, top_n=10)
        seo_patterns = self._aggregate_seo_patterns(analyses)

        # Calculate average effectiveness
        avg_effectiveness = sum(a.effectiveness_score for a in analyses) / len(analyses)

        # Generate comprehensive markdown report using Gemini
        markdown_report = self._generate_synthesis_report(
            topic=topic,
            num_videos=len(analyses),
            top_hooks=top_hooks,
            optimal_structure=optimal_structure,
            effective_ctas=effective_ctas,
            key_vocabulary=key_vocabulary,
            notable_techniques=notable_techniques,
            seo_patterns=seo_patterns,
            avg_effectiveness=avg_effectiveness,
        )

        logger.info(f"Synthesis complete for {len(analyses)} videos")

        return PatternSynthesis(
            topic=topic,
            num_videos_analyzed=len(analyses),
            top_hooks=top_hooks,
            optimal_structure=optimal_structure,
            effective_ctas=effective_ctas,
            key_vocabulary=key_vocabulary,
            notable_techniques=notable_techniques,
            seo_patterns=seo_patterns,
            average_effectiveness=avg_effectiveness,
            synthesis_timestamp=datetime.now(UTC),
            markdown_report=markdown_report,
        )

    def _extract_top_hooks(
        self,
        analyses: list[VideoAnalysis],
        top_n: int = 10,
    ) -> list[dict]:
        """Extract top N hooks weighted by effectiveness score.

        Args:
            analyses: List of video analyses
            top_n: Number of top hooks to extract

        Returns:
            List of dicts with hook info sorted by weighted score
        """
        weighted_hooks = []

        for analysis in analyses:
            if not analysis.hook_text:
                continue

            # Weight hook by video quality score
            weighted_score = analysis.effectiveness_score
            weighted_hooks.append(
                {
                    "text": analysis.hook_text[:200],  # Truncate long hooks
                    "type": analysis.hook_type,
                    "effectiveness": analysis.hook_effectiveness,
                    "weighted_score": weighted_score,
                    "duration_seconds": analysis.hook_end - analysis.hook_start,
                    "video_title": analysis.video.title,
                }
            )

        # Sort by weighted score descending
        weighted_hooks.sort(key=lambda x: x["weighted_score"], reverse=True)

        return weighted_hooks[:top_n]

    def _calculate_optimal_structure(self, analyses: list[VideoAnalysis]) -> dict:
        """Calculate optimal video structure from weighted averages.

        Args:
            analyses: List of video analyses

        Returns:
            Dict with structural metrics
        """
        # Weighted averages
        hook_durations = [a.hook_end - a.hook_start for a in analyses if a.hook_end > 0]
        intro_ends = [a.intro_end for a in analyses if a.intro_end > 0]
        num_sections = [len(a.sections) for a in analyses if a.sections]
        conclusion_starts = [a.conclusion_start for a in analyses if a.conclusion_start > 0]

        def weighted_avg(values: list, weights: list) -> float:
            """Calculate weighted average."""
            if not values:
                return 0.0
            return sum(v * w for v, w in zip(values, weights, strict=True)) / sum(weights)

        # Use effectiveness_score as weights
        weights = [a.effectiveness_score for a in analyses]

        return {
            "hook_duration_avg": (
                weighted_avg(hook_durations, weights[: len(hook_durations)])
                if hook_durations
                else 15.0
            ),
            "intro_end_avg": (
                weighted_avg(intro_ends, weights[: len(intro_ends)]) if intro_ends else 60.0
            ),
            "num_sections_mode": (
                max(set(num_sections), key=num_sections.count) if num_sections else 3
            ),
            "conclusion_start_avg": (
                weighted_avg(conclusion_starts, weights[: len(conclusion_starts)])
                if conclusion_starts
                else 0.0
            ),
            "total_videos": len(analyses),
        }

    def _extract_effective_ctas(
        self,
        analyses: list[VideoAnalysis],
        top_n: int = 15,
    ) -> list[dict]:
        """Extract most effective CTAs by frequency and position.

        Args:
            analyses: List of video analyses
            top_n: Number of top CTAs to extract

        Returns:
            List of dicts with CTA info sorted by frequency
        """
        cta_counter = Counter()
        cta_details = {}

        for analysis in analyses:
            for cta in analysis.ctas:
                cta_text = cta.get("text", "")
                cta_type = cta.get("type", "unknown")
                key = f"{cta_type}:{cta_text}"

                cta_counter[key] += 1

                if key not in cta_details:
                    cta_details[key] = {
                        "text": cta_text,
                        "type": cta_type,
                        "positions": [],
                        "frequency": 0,
                    }

                # Track positions (timestamp as % of video duration)
                timestamp = cta.get("timestamp", 0)
                if isinstance(timestamp, str) and ":" in timestamp:
                    # Parse timestamp like "5:30" to seconds
                    parts = timestamp.split(":")
                    timestamp = int(parts[0]) * 60 + int(parts[1])

                if analysis.video.duration_seconds > 0:
                    position_percent = (timestamp / analysis.video.duration_seconds) * 100
                    cta_details[key]["positions"].append(position_percent)

        # Update frequencies and calculate average positions
        effective_ctas = []
        for key, count in cta_counter.most_common(top_n):
            details = cta_details[key]
            details["frequency"] = count
            details["avg_position_percent"] = (
                sum(details["positions"]) / len(details["positions"])
                if details["positions"]
                else 0.0
            )
            del details["positions"]  # Remove raw positions
            effective_ctas.append(details)

        return effective_ctas

    def _aggregate_vocabulary(self, analyses: list[VideoAnalysis]) -> dict:
        """Aggregate vocabulary patterns across all videos.

        Args:
            analyses: List of video analyses

        Returns:
            Dict with aggregated vocabulary
        """
        technical_counter = Counter()
        phrases_counter = Counter()
        transitions_counter = Counter()

        for analysis in analyses:
            # Weight by effectiveness score
            weight = int(analysis.effectiveness_score)

            for term in analysis.technical_terms:
                technical_counter[term] += weight

            for phrase in analysis.common_phrases:
                phrases_counter[phrase] += weight

            for transition in analysis.transition_phrases:
                transitions_counter[transition] += weight

        return {
            "technical_terms": [
                {"term": term, "frequency": count}
                for term, count in technical_counter.most_common(20)
            ],
            "common_phrases": [
                {"phrase": phrase, "frequency": count}
                for phrase, count in phrases_counter.most_common(15)
            ],
            "transition_phrases": [
                {"phrase": phrase, "frequency": count}
                for phrase, count in transitions_counter.most_common(10)
            ],
        }

    def _extract_notable_techniques(
        self,
        analyses: list[VideoAnalysis],
        top_n: int = 10,
    ) -> list[dict]:
        """Extract notable techniques from high-quality videos.

        Args:
            analyses: List of video analyses
            top_n: Number of techniques to extract

        Returns:
            List of dicts with technique info
        """
        technique_counter = Counter()
        technique_descriptions = {}

        for analysis in analyses:
            # Only consider techniques from high-quality videos (score >= 3.5)
            if analysis.effectiveness_score < 3.5:
                continue

            for technique in analysis.techniques:
                name = technique.get("name", "")
                if not name:
                    continue

                technique_counter[name] += 1

                if name not in technique_descriptions:
                    technique_descriptions[name] = technique.get("description", "")

        notable = []
        for name, count in technique_counter.most_common(top_n):
            notable.append(
                {
                    "name": name,
                    "description": technique_descriptions.get(name, ""),
                    "frequency": count,
                }
            )

        return notable

    def _aggregate_seo_patterns(self, analyses: list[VideoAnalysis]) -> dict:
        """Aggregate SEO keywords and tags across videos.

        Args:
            analyses: List of video analyses

        Returns:
            Dict with SEO patterns
        """
        keyword_counter = Counter()
        tag_counter = Counter()

        for analysis in analyses:
            # Weight by effectiveness score
            weight = int(analysis.effectiveness_score)

            for keyword in analysis.title_keywords:
                keyword_counter[keyword] += weight

            for tag in analysis.estimated_tags:
                tag_counter[tag] += weight

        return {
            "title_keywords": [
                {"keyword": kw, "frequency": count} for kw, count in keyword_counter.most_common(15)
            ],
            "estimated_tags": [
                {"tag": tag, "frequency": count} for tag, count in tag_counter.most_common(20)
            ],
        }

    def _generate_synthesis_report(
        self,
        topic: str,
        num_videos: int,
        top_hooks: list[dict],
        optimal_structure: dict,
        effective_ctas: list[dict],
        key_vocabulary: dict,
        notable_techniques: list[dict],
        seo_patterns: dict,
        avg_effectiveness: float,
    ) -> str:
        """Generate comprehensive markdown synthesis report using Gemini.

        Args:
            topic: Topic of synthesis
            num_videos: Number of videos analyzed
            top_hooks: Top hooks list
            optimal_structure: Optimal structure dict
            effective_ctas: Effective CTAs list
            key_vocabulary: Vocabulary dict
            notable_techniques: Notable techniques list
            seo_patterns: SEO patterns dict
            avg_effectiveness: Average effectiveness score

        Returns:
            Markdown formatted synthesis report
        """
        # Create structured data for Gemini
        synthesis_data = {
            "topic": topic,
            "num_videos": num_videos,
            "avg_effectiveness": avg_effectiveness,
            "top_hooks": top_hooks[:5],  # Top 5 for prompt
            "optimal_structure": optimal_structure,
            "effective_ctas": effective_ctas[:10],  # Top 10
            "key_vocabulary": {
                "technical_terms": key_vocabulary["technical_terms"][:10],
                "common_phrases": key_vocabulary["common_phrases"][:10],
            },
            "notable_techniques": notable_techniques[:5],
            "seo_patterns": {
                "title_keywords": seo_patterns["title_keywords"][:10],
                "estimated_tags": seo_patterns["estimated_tags"][:10],
            },
        }

        prompt = f"""Genera un informe de síntesis profesional en Markdown basado en el análisis de {num_videos} videos exitosos de YouTube sobre "{topic}".

**DATOS DE LA SÍNTESIS**:
```json
{json.dumps(synthesis_data, indent=2, ensure_ascii=False)}
```

**ESTRUCTURA DEL INFORME** (en Markdown):

# Síntesis de Patrones: {topic}

## 📊 Resumen Ejecutivo
- Videos analizados: {num_videos}
- Efectividad promedio: {avg_effectiveness:.1f}/5.0
- Fecha: [fecha actual]

## 🎯 Top 5 Hooks Más Efectivos

Para cada hook incluye:
- Texto exacto del hook
- Tipo (question/statistic/promise/problem)
- Por qué es efectivo
- Duración promedio

## 🏗️ Estructura Óptima del Video

Basado en promedios ponderados:
- Duración del hook: X-Y segundos
- Final de intro: X-Y segundos
- Número de secciones: X (moda)
- Inicio de conclusión: minuto X

## 📣 CTAs Más Efectivos

Top 10 CTAs ordenados por frecuencia:
- Tipo de CTA
- Texto exacto
- Posición promedio en el video (%)
- Frecuencia de aparición

## 📚 Vocabulario Clave

### Términos Técnicos (Top 10)
Lista con frecuencia de uso

### Frases Comunes (Top 10)
Expresiones características con frecuencia

## 🎨 Técnicas Destacables

Top 5 técnicas de videos de alta calidad:
- Nombre de la técnica
- Descripción de uso
- Frecuencia de aparición

## 🔍 Patrones SEO

### Keywords en Títulos (Top 10)
Palabras clave más frecuentes

### Tags Recomendados (Top 10)
Tags basados en análisis

## 💡 Recomendaciones Finales

Basado en todos los patrones, proporciona:
1. 3 puntos clave para replicar el éxito
2. Advertencias (qué evitar)
3. Oportunidades de diferenciación

---

**Genera el informe completo en Markdown siguiendo esta estructura.**
"""

        try:
            response = self.model.generate_content(prompt)
            report = response.text.strip()
            logger.info("Synthesis report generated successfully")
            return report

        except Exception as e:
            logger.warning(f"Failed to generate Gemini synthesis report: {e}")
            # Fallback: simple markdown report
            return self._create_fallback_report(
                topic, num_videos, top_hooks, optimal_structure, effective_ctas, avg_effectiveness
            )

    def _create_fallback_report(
        self,
        topic: str,
        num_videos: int,
        top_hooks: list[dict],
        optimal_structure: dict,
        effective_ctas: list[dict],
        avg_effectiveness: float,
    ) -> str:
        """Create basic markdown report without Gemini.

        Args:
            topic: Topic name
            num_videos: Number of videos
            top_hooks: Top hooks
            optimal_structure: Structure data
            effective_ctas: CTAs data
            avg_effectiveness: Average score

        Returns:
            Basic markdown report
        """
        report = f"""# Síntesis de Patrones: {topic}

## 📊 Resumen Ejecutivo
- Videos analizados: {num_videos}
- Efectividad promedio: {avg_effectiveness:.1f}/5.0
- Fecha: {datetime.now(UTC).strftime("%Y-%m-%d")}

## 🎯 Top Hooks

"""
        for i, hook in enumerate(top_hooks[:5], 1):
            report += f"{i}. **{hook['type'].title()}**: {hook['text'][:100]}...\n"

        report += f"""

## 🏗️ Estructura Óptima
- Hook duration: {optimal_structure["hook_duration_avg"]:.0f} segundos
- Intro end: {optimal_structure["intro_end_avg"]:.0f} segundos
- Sections: {optimal_structure["num_sections_mode"]}

## 📣 Top CTAs

"""
        for i, cta in enumerate(effective_ctas[:5], 1):
            report += f"{i}. **{cta['type'].title()}** ({cta['frequency']}x): {cta['text']}\n"

        return report
