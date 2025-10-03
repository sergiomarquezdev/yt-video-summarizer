"""Query Optimizer - Extracts SEO keywords from user input using Gemini."""

import json
import logging
from dataclasses import dataclass

import google.generativeai as genai

from yt_transcriber.config import settings


logger = logging.getLogger(__name__)


@dataclass
class OptimizedQuery:
    """Result of query optimization."""

    original_query: str
    optimized_query: str
    keywords: list[str]
    estimated_minutes: int | None = None


class QueryOptimizer:
    """Optimizes user queries for YouTube search using Gemini."""

    def __init__(self, model_name: str | None = None):
        """Initialize the query optimizer.

        Args:
            model_name: Gemini model name (defaults to config setting)
        """
        self.model_name = model_name or settings.GEMINI_PRO_MODEL
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.model_name)

    def optimize(self, user_query: str) -> OptimizedQuery:
        """Optimize a user query for YouTube search.

        Args:
            user_query: Raw user input (e.g., "crear un video sobre Python")

        Returns:
            OptimizedQuery with keywords and search-ready query
        """
        logger.info(f"Optimizing query: {user_query}")

        try:
            # Create structured prompt for Gemini
            prompt = self._create_optimization_prompt(user_query)

            # Call Gemini API
            response = self.model.generate_content(prompt)

            # Parse JSON response
            result = self._parse_response(response.text, user_query)

            logger.info(f"Query optimized: '{user_query}' → '{result.optimized_query}'")
            return result

        except Exception as e:
            logger.warning(f"Query optimization failed: {e}. Using original query as fallback.")
            return self._create_fallback_result(user_query)

    def _create_optimization_prompt(self, user_query: str) -> str:
        """Create a structured prompt for query optimization.

        Args:
            user_query: Original user query

        Returns:
            Prompt string for Gemini
        """
        return f"""Eres un experto en SEO de YouTube. Analiza la siguiente idea de video y extrae información optimizada para búsqueda.

Idea del usuario: "{user_query}"

Tu tarea:
1. Extraer las keywords principales (eliminar stopwords como "crear", "hacer", "con", "de", "en")
2. Añadir sinónimos relevantes para búsqueda (tutorial, guide, curso, proyecto, etc.)
3. Generar una query optimizada para YouTube search
4. Estimar la duración ideal del video en minutos (basado en el tema)

IMPORTANTE: Responde SOLO con JSON válido, sin markdown ni explicaciones.

Formato de respuesta:
{{
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "optimized_query": "optimized search query",
    "estimated_minutes": 15
}}

Ejemplos:
- Input: "crear proyecto con FastAPI en Python"
  Output: {{"keywords": ["FastAPI", "Python", "REST API", "proyecto", "backend"], "optimized_query": "FastAPI Python tutorial proyecto REST API", "estimated_minutes": 20}}

- Input: "cómo hacer deploy de app React en Vercel"
  Output: {{"keywords": ["React", "Vercel", "deploy", "production", "hosting"], "optimized_query": "React Vercel deploy production tutorial", "estimated_minutes": 15}}

Ahora analiza: "{user_query}"
"""

    def _parse_response(self, response_text: str, original_query: str) -> OptimizedQuery:
        """Parse Gemini's JSON response.

        Args:
            response_text: Raw response from Gemini
            original_query: Original user query for fallback

        Returns:
            OptimizedQuery object
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

            return OptimizedQuery(
                original_query=original_query,
                optimized_query=data["optimized_query"],
                keywords=data["keywords"],
                estimated_minutes=data.get("estimated_minutes"),
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse Gemini response: {e}. Response: {response_text}")
            return self._create_fallback_result(original_query)

    def _create_fallback_result(self, original_query: str) -> OptimizedQuery:
        """Create fallback result when optimization fails.

        Args:
            original_query: Original user query

        Returns:
            OptimizedQuery with original query as optimized query
        """
        # Simple keyword extraction: split and filter common stopwords
        stopwords = {
            "crear",
            "hacer",
            "cómo",
            "como",
            "de",
            "del",
            "la",
            "el",
            "en",
            "con",
            "un",
            "una",
            "para",
            "por",
            "sobre",
            "que",
            "create",
            "make",
            "how",
            "to",
            "a",
            "an",
            "the",
            "in",
            "on",
            "with",
            "for",
            "about",
            "of",
        }

        words = original_query.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]

        return OptimizedQuery(
            original_query=original_query,
            optimized_query=original_query,  # Use original as fallback
            keywords=keywords if keywords else [original_query],
            estimated_minutes=15,  # Default duration
        )
