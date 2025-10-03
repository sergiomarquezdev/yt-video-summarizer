"""Query Optimizer - Extracts SEO keywords from user input using Gemini."""

from dataclasses import dataclass

import google.generativeai as genai

from yt_transcriber.config import settings


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
        # TODO: Implement Gemini-based query optimization
        # Extract:
        # - Core topic
        # - SEO keywords
        # - Estimated video duration preference
        # - Optimized search query
        raise NotImplementedError("Query optimization not yet implemented")
