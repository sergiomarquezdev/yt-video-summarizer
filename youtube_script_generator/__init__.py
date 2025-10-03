"""
YouTube Script Generator

Sistema inteligente que genera guiones optimizados para YouTube aprendiendo
de videos exitosos en tiempo real.

Workflow:
1. Usuario proporciona idea de video
2. Sistema optimiza query de búsqueda con Gemini
3. Busca top N videos en YouTube con yt-dlp
4. Transcribe videos con Whisper (CUDA)
5. Analiza cada video extrayendo patrones (hooks, CTAs, estructura)
6. Sintetiza los análisis en documento de mejores prácticas
7. Genera guión optimizado usando síntesis como contexto
8. Traduce guión al español (opcional)

Módulos:
- query_optimizer: Optimiza búsqueda con Gemini
- youtube_searcher: Busca videos con yt-dlp
- batch_processor: Download + transcribe múltiples videos
- pattern_analyzer: Analiza patrones de cada video
- synthesizer: Sintetiza N análisis → 1 documento
- script_generator: Genera guión final
- translator: Traduce guiones a español
- models: Dataclasses compartidas
"""

from youtube_script_generator.batch_processor import BatchProcessor
from youtube_script_generator.models import (
    GeneratedScript,
    PatternSynthesis,
    VideoAnalysis,
    VideoTranscript,
    YouTubeVideo,
)
from youtube_script_generator.pattern_analyzer import PatternAnalyzer
from youtube_script_generator.query_optimizer import OptimizedQuery, QueryOptimizer
from youtube_script_generator.script_generator import ScriptGenerator
from youtube_script_generator.synthesizer import PatternSynthesizer
from youtube_script_generator.translator import ScriptTranslator
from youtube_script_generator.youtube_searcher import YouTubeSearcher


__version__ = "0.2.0"
__author__ = "Sergio Marquez"

__all__ = [
    # Models
    "YouTubeVideo",
    "VideoTranscript",
    "VideoAnalysis",
    "PatternSynthesis",
    "GeneratedScript",
    "OptimizedQuery",
    # Components
    "QueryOptimizer",
    "YouTubeSearcher",
    "BatchProcessor",
    "PatternAnalyzer",
    "PatternSynthesizer",
    "ScriptGenerator",
    "ScriptTranslator",
]
