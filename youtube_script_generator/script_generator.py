"""Script Generator - Generates optimized YouTube scripts using Gemini."""

import logging
from datetime import UTC, datetime

import google.generativeai as genai

from youtube_script_generator.models import GeneratedScript, PatternSynthesis
from yt_transcriber.config import settings


logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Generates YouTube scripts based on synthesized patterns.

    This class creates professional YouTube scripts by applying patterns
    learned from successful videos. It generates complete scripts with
    hooks, structure, CTAs, and SEO optimization.

    Features:
    - Pattern-based script generation
    - Duration targeting with word count estimation
    - SEO optimization (title, description, tags)
    - Timestamp annotations
    - Quality estimation
    """

    # Average speaking rate for YouTube videos (words per minute)
    WORDS_PER_MINUTE = 150

    def __init__(self, model_name: str | None = None):
        """Initialize the script generator.

        Args:
            model_name: Gemini model name (defaults to config setting)
        """
        self.model_name = model_name or settings.GEMINI_PRO_MODEL
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.model_name)

    def generate(
        self,
        synthesis: PatternSynthesis,
        user_idea: str,
        duration_minutes: int = 10,
        style_preference: str | None = None,
    ) -> GeneratedScript:
        """Generate a YouTube script based on learned patterns.

        Args:
            synthesis: PatternSynthesis with learned patterns from successful videos
            user_idea: User's video idea/topic
            duration_minutes: Target duration in minutes (default: 10)
            style_preference: Optional style guidance (e.g., "educational", "entertaining")

        Returns:
            GeneratedScript with complete script and SEO metadata

        Raises:
            ValueError: If synthesis or user_idea is invalid
        """
        if not user_idea or not user_idea.strip():
            raise ValueError("user_idea cannot be empty")

        logger.info(f"Generating script for: {user_idea} (target: {duration_minutes} min)")

        # Create generation prompt with synthesis context
        prompt = self._create_generation_prompt(
            synthesis=synthesis,
            user_idea=user_idea,
            duration_minutes=duration_minutes,
            style_preference=style_preference,
        )

        try:
            # Generate script with Gemini
            response = self.model.generate_content(prompt)
            script_text = response.text.strip()

            # Parse response (expecting JSON or Markdown)
            script_data = self._parse_script_response(script_text, user_idea, synthesis)

            logger.info(f"Script generated successfully: {script_data['word_count']} words")

            return GeneratedScript(
                user_idea=user_idea,
                script_markdown=script_data["script_markdown"],
                estimated_duration_minutes=script_data["estimated_duration_minutes"],
                word_count=script_data["word_count"],
                seo_title=script_data["seo_title"],
                seo_description=script_data["seo_description"],
                seo_tags=script_data["seo_tags"],
                synthesis_used=synthesis.topic,
                num_reference_videos=synthesis.num_videos_analyzed,
                generation_timestamp=datetime.now(UTC),
                cost_usd=0.0,  # TODO: Calculate based on token usage
                estimated_quality_score=script_data["estimated_quality_score"],
            )

        except Exception as e:
            logger.warning(f"Failed to generate script with Gemini: {e}")
            # Fallback: generate basic script template
            return self._create_fallback_script(user_idea, synthesis, duration_minutes)

    def _create_generation_prompt(
        self,
        synthesis: PatternSynthesis,
        user_idea: str,
        duration_minutes: int,
        style_preference: str | None,
    ) -> str:
        """Create comprehensive generation prompt with synthesis context.

        Args:
            synthesis: PatternSynthesis with learned patterns
            user_idea: User's video idea
            duration_minutes: Target duration
            style_preference: Optional style guidance

        Returns:
            Structured prompt for Gemini
        """
        # Calculate target word count
        target_words = duration_minutes * self.WORDS_PER_MINUTE

        # Extract key patterns from synthesis for prompt
        top_hook_examples = [h["text"][:100] for h in synthesis.top_hooks[:3]]
        top_ctas = [c["text"] for c in synthesis.effective_ctas[:5]]
        key_terms = [t["term"] for t in synthesis.key_vocabulary.get("technical_terms", [])[:10]]
        key_phrases = [p["phrase"] for p in synthesis.key_vocabulary.get("common_phrases", [])[:5]]

        style_guidance = f"\n**ESTILO PREFERIDO**: {style_preference}" if style_preference else ""

        prompt = f"""Eres un guionista profesional de YouTube. Crea un guion completo y profesional para un video sobre:

**TEMA DEL VIDEO**: {user_idea}

**CONTEXTO**: Has analizado {synthesis.num_videos_analyzed} videos exitosos sobre temas relacionados.
La efectividad promedio de estos videos es {synthesis.average_effectiveness:.1f}/5.0.
{style_guidance}

**MEJORES PRÁCTICAS IDENTIFICADAS**:

1. **Hooks Más Efectivos** (inspírate en estos):
{chr(10).join(f'   - "{hook}"' for hook in top_hook_examples)}

2. **Estructura Óptima**:
   - Hook: {synthesis.optimal_structure.get("hook_duration_avg", 15):.0f} segundos
   - Intro: termina en {synthesis.optimal_structure.get("intro_end_avg", 60):.0f} segundos
   - Secciones: {synthesis.optimal_structure.get("num_sections_mode", 3)} secciones principales
   - Conclusión: comienza en minuto {synthesis.optimal_structure.get("conclusion_start_avg", 540) / 60:.0f}

3. **CTAs Efectivos** (usa 2-3 en momentos clave):
{chr(10).join(f'   - "{cta}"' for cta in top_ctas)}

4. **Vocabulario del Nicho**:
   - Términos clave: {", ".join(key_terms)}
   - Frases comunes: {", ".join(key_phrases)}

**REQUISITOS DEL GUION**:

- **Duración objetivo**: {duration_minutes} minutos (~{target_words} palabras)
- **Formato**: Markdown con timestamps [MM:SS]
- **Estructura**: Hook → Intro → {synthesis.optimal_structure.get("num_sections_mode", 3)} secciones → Conclusión
- **CTAs**: 2-3 CTAs en posiciones estratégicas (10%, 50%, 90% del video)
- **Tono**: Profesional pero accesible, usa vocabulario del nicho
- **Timestamps**: Incluye [MM:SS] al inicio de cada sección

**ESTRUCTURA DEL GUION** (en Markdown):

# [TÍTULO DEL VIDEO]

## [00:00] HOOK (primeros {synthesis.optimal_structure.get("hook_duration_avg", 15):.0f} segundos)
[Gancho impactante basado en los ejemplos de arriba - pregunta, estadística, o promesa]

## [00:15] INTRODUCCIÓN
[Presentación breve, qué aprenderán, por qué es importante]
[Primer CTA: like/subscribe]

## [01:00] SECCIÓN 1: [Título]
[Contenido principal con ejemplos]

## [XX:XX] SECCIÓN 2: [Título]
[Contenido con detalles técnicos]
[Segundo CTA: comentar o interactuar]

## [XX:XX] SECCIÓN 3: [Título]
[Más contenido relevante]

## [XX:XX] CONCLUSIÓN
[Resumen de puntos clave]
[CTA final: suscripción y próximo video]

---

**SEO OPTIMIZATION** (genera también):

**TÍTULO** (50-70 caracteres, keywords al inicio):
[Título optimizado para SEO]

**DESCRIPCIÓN** (150-200 palabras):
[Descripción atractiva con keywords del análisis]

**TAGS** (15-20 tags):
[Lista de tags separados por comas basados en keywords del análisis]

---

**INSTRUCCIONES FINALES**:
1. Aplica los patrones identificados en los videos exitosos
2. Usa el vocabulario característico del nicho
3. Inserta CTAs en posiciones óptimas basadas en el análisis
4. Mantén el tono y estilo de los videos exitosos
5. Asegura que el contenido sea valioso y accionable

**Genera el guion completo ahora en formato Markdown.**
"""

        return prompt

    def _parse_script_response(
        self,
        response_text: str,
        user_idea: str,
        synthesis: PatternSynthesis,
    ) -> dict:
        """Parse Gemini's script response.

        Args:
            response_text: Raw response from Gemini
            user_idea: Original user idea
            synthesis: Synthesis used for context

        Returns:
            Dict with parsed script components
        """
        # Clean response (remove markdown code blocks if present)
        clean_text = response_text.strip()
        if clean_text.startswith("```markdown"):
            clean_text = clean_text[11:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        # Extract SEO components (if present in structured format)
        seo_title = self._extract_seo_title(clean_text, user_idea, synthesis)
        seo_description = self._extract_seo_description(clean_text, user_idea, synthesis)
        seo_tags = self._extract_seo_tags(clean_text, synthesis)

        # Calculate word count
        word_count = len(clean_text.split())

        # Estimate duration from word count
        estimated_duration = max(1, round(word_count / self.WORDS_PER_MINUTE))

        # Estimate quality score (based on length, structure, SEO)
        quality_score = self._estimate_quality_score(clean_text, word_count, seo_title, seo_tags)

        return {
            "script_markdown": clean_text,
            "word_count": word_count,
            "estimated_duration_minutes": estimated_duration,
            "seo_title": seo_title,
            "seo_description": seo_description,
            "seo_tags": seo_tags,
            "estimated_quality_score": quality_score,
        }

    def _extract_seo_title(
        self, script_text: str, user_idea: str, synthesis: PatternSynthesis
    ) -> str:
        """Extract or generate SEO-optimized title.

        Args:
            script_text: Full script text
            user_idea: Original idea
            synthesis: Synthesis for keywords

        Returns:
            SEO-optimized title
        """
        # Look for explicit title markers
        for marker in ["**TÍTULO**:", "TÍTULO:", "# "]:
            if marker in script_text:
                # Extract line after marker
                lines = script_text.split("\n")
                for i, line in enumerate(lines):
                    if marker in line and i + 1 < len(lines):
                        title = lines[i + 1].strip()
                        # Clean markdown formatting
                        title = title.replace("[", "").replace("]", "")
                        title = title.strip("#").strip()
                        if len(title) > 10:  # Reasonable title length
                            return title[:70]  # Max 70 chars

        # Fallback: use first heading from script
        lines = script_text.split("\n")
        for line in lines:
            if line.startswith("# "):
                title = line.strip("#").strip()
                return title[:70]

        # Final fallback: capitalize user idea with top keyword
        top_keyword = ""
        if synthesis.seo_patterns.get("title_keywords"):
            top_keyword = synthesis.seo_patterns["title_keywords"][0]["keyword"]

        return f"{top_keyword} - {user_idea}"[:70] if top_keyword else user_idea[:70]

    def _extract_seo_description(
        self, script_text: str, user_idea: str, synthesis: PatternSynthesis
    ) -> str:
        """Extract or generate SEO description.

        Args:
            script_text: Full script text
            user_idea: Original idea
            synthesis: Synthesis for context

        Returns:
            SEO description
        """
        # Look for explicit description marker
        if "**DESCRIPCIÓN**:" in script_text:
            parts = script_text.split("**DESCRIPCIÓN**:")
            if len(parts) > 1:
                # Extract text until next section
                desc_section = parts[1].split("**TAGS**")[0].split("---")[0]
                desc = desc_section.strip()[:500]
                if len(desc) > 50:
                    return desc

        # Fallback: generate from script intro
        lines = script_text.split("\n")
        intro_lines = []
        for line in lines[5:20]:  # Skip title, look in intro area
            if line.strip() and not line.startswith("#") and not line.startswith("["):
                intro_lines.append(line.strip())
                if len(" ".join(intro_lines)) > 150:
                    break

        if intro_lines:
            return " ".join(intro_lines)[:500]

        # Final fallback: simple description
        return f"Video sobre {user_idea}. Basado en análisis de {synthesis.num_videos_analyzed} videos exitosos."

    def _extract_seo_tags(self, script_text: str, synthesis: PatternSynthesis) -> list[str]:
        """Extract or generate SEO tags.

        Args:
            script_text: Full script text
            synthesis: Synthesis for keywords

        Returns:
            List of SEO tags
        """
        # Look for explicit tags marker
        if "**TAGS**:" in script_text:
            parts = script_text.split("**TAGS**:")
            if len(parts) > 1:
                tags_section = parts[1].split("---")[0].split("\n")[0]
                tags = [t.strip() for t in tags_section.split(",")]
                tags = [t for t in tags if t and len(t) > 2]
                if tags:
                    return tags[:20]

        # Fallback: use synthesis keywords
        tags = []
        if synthesis.seo_patterns.get("title_keywords"):
            tags.extend(kw["keyword"] for kw in synthesis.seo_patterns["title_keywords"][:15])

        if synthesis.seo_patterns.get("estimated_tags"):
            tags.extend(tag["tag"] for tag in synthesis.seo_patterns["estimated_tags"][:10])

        # Remove duplicates, keep order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)

        return unique_tags[:20]

    def _estimate_quality_score(
        self, script_text: str, word_count: int, seo_title: str, seo_tags: list[str]
    ) -> int:
        """Estimate script quality score (1-100).

        Args:
            script_text: Full script text
            word_count: Total words
            seo_title: SEO title
            seo_tags: SEO tags

        Returns:
            Quality score (1-100)
        """
        score = 50  # Base score

        # Length appropriateness (±20 points)
        if 500 <= word_count <= 2000:
            score += 20
        elif 300 <= word_count < 500 or 2000 < word_count <= 3000:
            score += 10

        # Structure presence (±15 points)
        if "[00:00]" in script_text or "[0:00]" in script_text:
            score += 5  # Has timestamps
        if "##" in script_text:
            score += 5  # Has sections
        section_count = script_text.count("##")
        if 3 <= section_count <= 7:
            score += 5  # Good section count

        # SEO optimization (±15 points)
        if seo_title and len(seo_title) >= 20:
            score += 5
        if len(seo_tags) >= 10:
            score += 5
        if len(seo_tags) >= 15:
            score += 5

        return min(100, max(1, score))

    def _create_fallback_script(
        self,
        user_idea: str,
        synthesis: PatternSynthesis,
        duration_minutes: int,
    ) -> GeneratedScript:
        """Create basic script template without Gemini.

        Args:
            user_idea: User's idea
            synthesis: Synthesis for context
            duration_minutes: Target duration

        Returns:
            Basic GeneratedScript
        """
        target_words = duration_minutes * self.WORDS_PER_MINUTE

        # Get top hook if available
        top_hook = synthesis.top_hooks[0]["text"][:150] if synthesis.top_hooks else "¡Bienvenidos!"

        script = f"""# {user_idea}

## [00:00] HOOK
{top_hook}

## [00:15] INTRODUCCIÓN
En este video vamos a explorar {user_idea}.

## [01:00] CONTENIDO PRINCIPAL
[Desarrolla el tema aquí - aproximadamente {target_words} palabras]

## [XX:XX] CONCLUSIÓN
Eso es todo por hoy. ¡Gracias por ver!

---

**Nota**: Este es un guion básico generado automáticamente.
Basado en análisis de {synthesis.num_videos_analyzed} videos exitosos.
"""

        return GeneratedScript(
            user_idea=user_idea,
            script_markdown=script,
            estimated_duration_minutes=duration_minutes,
            word_count=len(script.split()),
            seo_title=user_idea[:70],
            seo_description=f"Video sobre {user_idea}",
            seo_tags=["tutorial", "guía", "español"],
            synthesis_used=synthesis.topic,
            num_reference_videos=synthesis.num_videos_analyzed,
            generation_timestamp=datetime.now(UTC),
            cost_usd=0.0,
            estimated_quality_score=50,
        )
