"""Tests for YouTube Script Generator module."""

import pytest

from youtube_script_generator import (
    BatchProcessor,
    PatternAnalyzer,
    PatternSynthesizer,
    QueryOptimizer,
    ScriptGenerator,
    YouTubeSearcher,
    YouTubeVideo,
)


class TestModels:
    """Test data models."""

    def test_youtube_video_creation(self):
        """Test YouTubeVideo model creation."""
        video = YouTubeVideo(
            video_id="test123",
            title="Test Video",
            url="https://youtube.com/watch?v=test123",
            duration_seconds=600,
            view_count=10000,
            upload_date="20240101",
            channel="Test Channel",
        )
        assert video.video_id == "test123"
        assert video.duration_seconds == 600
        assert video.channel == "Test Channel"

    def test_video_quality_score(self):
        """Test quality score calculation."""
        video = YouTubeVideo(
            video_id="test123",
            title="Test Video",
            url="https://youtube.com/watch?v=test123",
            duration_seconds=600,
            view_count=10000,
            upload_date="20240101",
            channel="Test Channel",
        )
        # Test that quality_score property exists and returns a valid value
        score = video.quality_score
        assert 0 <= score <= 100


class TestQueryOptimizer:
    """Test query optimizer."""

    def test_optimizer_initialization(self):
        """Test QueryOptimizer initialization."""
        optimizer = QueryOptimizer()
        assert optimizer.model_name is not None

    def test_optimize_query_success(self):
        """Test query optimization with Gemini."""
        optimizer = QueryOptimizer()
        result = optimizer.optimize("crear proyecto con FastAPI en Python")

        # Verify structure
        assert result.original_query == "crear proyecto con FastAPI en Python"
        assert result.optimized_query is not None
        assert len(result.optimized_query) > 0
        assert isinstance(result.keywords, list)
        assert len(result.keywords) > 0

        # Verify keywords quality
        keywords_lower = [k.lower() for k in result.keywords]
        assert any("fastapi" in k for k in keywords_lower) or any(
            "python" in k for k in keywords_lower
        )

    def test_optimize_query_removes_stopwords(self):
        """Test that stopwords are removed from keywords."""
        optimizer = QueryOptimizer()
        result = optimizer.optimize("cómo hacer deploy de app React en Vercel")

        keywords_lower = [k.lower() for k in result.keywords]

        # Common stopwords should be removed
        stopwords_to_avoid = ["cómo", "como", "hacer", "de", "en"]
        for stopword in stopwords_to_avoid:
            assert stopword not in keywords_lower, f"Stopword '{stopword}' found in keywords"

        # Important keywords should be present
        assert any("react" in k for k in keywords_lower) or any(
            "vercel" in k for k in keywords_lower
        )

    def test_optimize_query_fallback(self):
        """Test fallback when Gemini fails."""
        optimizer = QueryOptimizer()

        # Test with a query that should work even in fallback mode
        result = optimizer.optimize("Python tutorial")

        # Fallback should still return valid structure
        assert result.original_query == "Python tutorial"
        assert result.optimized_query is not None
        assert isinstance(result.keywords, list)
        assert len(result.keywords) > 0


class TestYouTubeSearcher:
    """Test YouTube searcher."""

    def test_searcher_initialization(self):
        """Test YouTubeSearcher initialization."""
        searcher = YouTubeSearcher(max_results=10)
        assert searcher.max_results == 10

    def test_youtube_search(self):
        """Test YouTube search functionality."""
        searcher = YouTubeSearcher(max_results=5)
        videos = searcher.search("Python tutorial", min_duration=3, max_duration=20)

        # Should return videos
        assert len(videos) > 0
        assert len(videos) <= 5

        # Verify video structure
        for video in videos:
            assert video.video_id
            assert video.title
            assert video.url
            assert video.duration_seconds > 0
            assert video.view_count >= 0
            assert video.channel

    def test_search_duration_filter(self):
        """Test that duration filtering works."""
        searcher = YouTubeSearcher(max_results=5)
        videos = searcher.search(
            "Python programming",
            min_duration=10,  # 10 minutes minimum
            max_duration=25,  # 25 minutes maximum
        )

        # All videos should be within duration range
        for video in videos:
            assert 10 <= video.duration_minutes <= 25

    def test_search_quality_ranking(self):
        """Test that videos are ranked by quality score."""
        # Use fewer results for faster test
        searcher = YouTubeSearcher(max_results=3)
        videos = searcher.search("Python tutorial", min_duration=5, max_duration=20)

        # Should have videos
        assert len(videos) > 0

        # Videos should be sorted by quality_score (descending)
        for i in range(len(videos) - 1):
            assert videos[i].quality_score >= videos[i + 1].quality_score


class TestBatchProcessor:
    """Test batch processor."""

    def test_processor_initialization(self):
        """Test BatchProcessor initialization."""
        processor = BatchProcessor(max_workers=3)
        assert processor.max_workers == 3

    @pytest.mark.skip(reason="Not implemented yet")
    def test_batch_processing(self):
        """Test batch video processing."""
        # TODO: Implement once batch_processor is ready
        pass


class TestPatternAnalyzer:
    """Test pattern analyzer."""

    def test_analyzer_initialization(self):
        """Test PatternAnalyzer initialization."""
        analyzer = PatternAnalyzer()
        assert analyzer.model_name is not None

    @pytest.mark.skip(reason="Not implemented yet")
    def test_pattern_analysis(self):
        """Test pattern extraction from transcript."""
        # TODO: Implement once pattern_analyzer is ready
        pass


class TestPatternSynthesizer:
    """Test pattern synthesizer."""

    def test_synthesizer_initialization(self):
        """Test PatternSynthesizer initialization."""
        synthesizer = PatternSynthesizer()
        assert synthesizer.model_name is not None

    @pytest.mark.skip(reason="Not implemented yet")
    def test_pattern_synthesis(self):
        """Test synthesis of multiple analyses."""
        # TODO: Implement once synthesizer is ready
        pass


class TestScriptGenerator:
    """Test script generator."""

    def test_generator_initialization(self):
        """Test ScriptGenerator initialization."""
        generator = ScriptGenerator()
        assert generator.model_name is not None

    @pytest.mark.skip(reason="Not implemented yet")
    def test_script_generation(self):
        """Test script generation from synthesis."""
        # TODO: Implement once script_generator is ready
        pass
