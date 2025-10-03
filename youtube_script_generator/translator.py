"""Script Translator - Translates generated scripts to Spanish with context preservation."""

import logging
import re

import google.generativeai as genai

from youtube_script_generator.models import GeneratedScript
from yt_transcriber.config import settings


logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Raised when translation fails."""

    pass


class ScriptTranslator:
    """Translates generated scripts to Spanish with intelligent term preservation."""

    def __init__(self):
        """Initialize the translator with Gemini API."""
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_PRO_MODEL)

    def translate_to_spanish(self, script: GeneratedScript) -> GeneratedScript:
        """Translate script from English to Spanish with context awareness.

        Args:
            script: Generated script in English

        Returns:
            New GeneratedScript object with Spanish translation

        Raises:
            TranslationError: If translation fails
        """
        logger.info(f"Translating script: {script.seo_title}")

        try:
            # Translate main script content
            translated_content = self._translate_content(
                script.script_markdown,
                script.seo_title,
            )

            # Translate SEO metadata
            translated_title = self._translate_seo_title(script.seo_title)
            translated_description = self._translate_seo_description(script.seo_description)

            # Keep original tags + add Spanish variants
            translated_tags = self._adapt_seo_tags(script.seo_tags)

            # Create new script object with translations
            translated_script = GeneratedScript(
                user_idea=script.user_idea,
                script_markdown=translated_content,
                estimated_duration_minutes=script.estimated_duration_minutes,
                word_count=len(translated_content.split()),
                seo_title=translated_title,
                seo_description=translated_description,
                seo_tags=translated_tags,
                synthesis_used=script.synthesis_used,
                num_reference_videos=script.num_reference_videos,
                generation_timestamp=script.generation_timestamp,
                cost_usd=script.cost_usd,
                estimated_quality_score=script.estimated_quality_score,
            )

            logger.info("Translation completed successfully")
            return translated_script

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise TranslationError(f"Failed to translate script: {e}") from e

    def _translate_content(self, content: str, title: str) -> str:
        """Translate script content with context preservation.

        Args:
            content: Original script content in English
            title: Script title for context

        Returns:
            Translated content in Spanish
        """
        prompt = f"""Translate the following YouTube script to Spanish with these requirements:

CONTEXT: This is a technical tutorial script about: "{title}"

TRANSLATION RULES:
1. Use NATURAL Spanish (Spain/Latin America neutral, mainly Spain)
2. Preserve technical terms in English when appropriate:
   - Software names (n8n, npm, Docker, etc.)
   - Programming terms (workflow, API, endpoint, deployment)
   - Commands and code blocks (keep unchanged)
3. Adapt expressions idiomatically, not literally
4. Maintain markdown formatting EXACTLY:
   - Headers (#, ##, ###)
   - Bold (**text**)
   - Lists (-, *)
   - Code blocks (```...```)
5. Adapt CTAs to Spanish style:
   - "Subscribe" → "Suscríbete"
   - "Like this video" → "Dale like si te gustó"
   - "Comment below" → "Déjame un comentario"
6. Keep professional but friendly tone
7. Preserve ALL timestamps if present

SCRIPT TO TRANSLATE:
{content}

OUTPUT: Only the translated script in Spanish, maintaining exact markdown structure."""

        try:
            response = self.model.generate_content(prompt)
            translated = response.text.strip()

            if not translated:
                raise TranslationError("Empty translation response from Gemini")

            return translated

        except Exception as e:
            logger.error(f"Content translation failed: {e}")
            # Fallback: return original with warning
            return f"⚠️ Translation failed. Original script below:\n\n{content}"

    def _translate_seo_title(self, title: str) -> str:
        """Translate SEO title to Spanish.

        Args:
            title: Original title in English

        Returns:
            Translated title in Spanish
        """
        prompt = f"""Translate this YouTube video title to Spanish.

RULES:
1. Keep it SEO-friendly and engaging
2. Preserve technical terms (software names, tools)
3. Maximum 100 characters
4. Natural Spanish (neutral for Spain/Latin America)

ORIGINAL TITLE:
{title}

OUTPUT: Only the translated title, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            translated = response.text.strip()

            # Remove quotes if Gemini added them
            translated = re.sub(r'^["\'](.*)["\']$', r"\1", translated)

            return translated if translated else title

        except Exception as e:
            logger.warning(f"Title translation failed, using original: {e}")
            return title

    def _translate_seo_description(self, description: str) -> str:
        """Translate SEO description to Spanish.

        Args:
            description: Original description in English

        Returns:
            Translated description in Spanish
        """
        prompt = f"""Translate this YouTube video description to Spanish.

RULES:
1. Keep it engaging and SEO-friendly
2. Preserve technical terms and tool names
3. Natural Spanish (neutral)
4. Maintain similar length (~150-300 chars)

ORIGINAL DESCRIPTION:
{description}

OUTPUT: Only the translated description, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            translated = response.text.strip()

            return translated if translated else description

        except Exception as e:
            logger.warning(f"Description translation failed, using original: {e}")
            return description

    def _adapt_seo_tags(self, tags: list[str]) -> list[str]:
        """Adapt SEO tags for Spanish audience.

        Args:
            tags: Original tags in English

        Returns:
            Combined list of original + Spanish translated tags
        """
        # Keep all original tags (technical terms are often searched in English)
        adapted_tags = tags.copy()

        # Common translations for generic terms
        translations = {
            "tutorial": "tutorial",
            "guide": "guía",
            "beginner": "principiante",
            "beginners": "principiantes",
            "installation": "instalación",
            "setup": "configuración",
            "how to": "cómo",
            "step by step": "paso a paso",
            "quick start": "inicio rápido",
            "getting started": "primeros pasos",
            "automation": "automatización",
            "workflow": "flujo de trabajo",
            "free": "gratis",
            "local": "local",
            "self-hosted": "auto-alojado",
        }

        # Add Spanish variants for translatable tags
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in translations and translations[tag_lower] not in adapted_tags:
                adapted_tags.append(translations[tag_lower])

        # Limit to 30 tags total (YouTube limit)
        return adapted_tags[:30]
