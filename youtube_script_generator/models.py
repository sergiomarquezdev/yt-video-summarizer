"""
Data models for YouTube Script Generator

Dataclasses compartidas entre módulos.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class YouTubeVideo:
    """Información de un video de YouTube obtenida de yt-dlp"""

    video_id: str
    title: str
    url: str
    duration_seconds: int
    view_count: int
    upload_date: str  # YYYYMMDD format
    channel: str
    like_count: int | None = None
    duration_preference: int | None = None  # Preferred duration for quality scoring

    @property
    def duration_minutes(self) -> float:
        """Duración en minutos"""
        return self.duration_seconds / 60

    @property
    def quality_score(self) -> float:
        """
        Calculate weighted quality score basado en métricas del video

        Factores:
        - View count (40%): Más views = más exitoso
        - Duration proximity to target (20%): Cerca del target es óptimo
        - Upload recency (20%): Más reciente = técnicas actuales
        - Completeness (20%): Tiene todos los datos
        """
        score = 0.0

        # Views (normalizado, peso 40%)
        # Asumimos 100K views como excelente (score 1.0)
        view_score = min(self.view_count / 100_000, 1.0)
        score += view_score * 0.4

        # Duration proximity to target (peso 20%)
        # Si hay preferencia, usarla; si no, asumir 15 min como óptimo
        target_duration = self.duration_preference or 15
        duration_diff = abs(self.duration_minutes - target_duration)

        if duration_diff <= 3:  # Within 3 minutes
            duration_score = 1.0
        elif duration_diff <= 6:  # Within 6 minutes
            duration_score = 0.7
        else:
            duration_score = 0.4
        score += duration_score * 0.2

        # Upload recency (peso 20%)
        # Último año = 1.0, más antiguo = menos score
        try:
            upload_year = int(self.upload_date[:4])
            current_year = datetime.now().year
            years_old = current_year - upload_year
            recency_score = max(1.0 - (years_old * 0.2), 0.3)
        except (ValueError, IndexError):
            recency_score = 0.5  # Default si no podemos parsear fecha
        score += recency_score * 0.2

        # Completeness (peso 20%)
        # Tiene likes, channel, etc.
        completeness_score = 1.0 if self.like_count is not None else 0.8
        score += completeness_score * 0.2

        return round(score * 5, 2)  # Escala 0-5


@dataclass
class VideoTranscript:
    """Transcripción de un video"""

    video: YouTubeVideo
    transcript_text: str
    word_timestamps: list[dict]
    language: str
    transcription_time_seconds: float


@dataclass
class VideoAnalysis:
    """Análisis de patrones extraídos de un video"""

    video: YouTubeVideo

    # Estructura
    hook_start: int  # segundos
    hook_end: int
    hook_text: str
    hook_type: str  # "question", "statistic", "promise", "problem"
    hook_effectiveness: str  # "high", "medium", "low"
    intro_end: int
    sections: list[dict]  # [{title, start, end, duration_min}]
    conclusion_start: int

    # CTAs
    ctas: list[dict]  # [{text, timestamp, position_percent, type}]

    # Vocabulario
    technical_terms: list[str]
    common_phrases: list[str]
    transition_phrases: list[str]

    # Técnicas
    techniques: list[dict]  # [{name, description}]

    # SEO
    title_keywords: list[str]
    estimated_tags: list[str]

    # Calidad (basada en metadata del video)
    effectiveness_score: float = field(init=False)

    # Raw
    raw_analysis: str  # JSON completo de Gemini

    def __post_init__(self):
        """Calculate effectiveness score from video metadata"""
        self.effectiveness_score = self.video.quality_score


@dataclass
class PatternSynthesis:
    """Síntesis de patrones de múltiples videos"""

    topic: str
    num_videos_analyzed: int

    # Top patterns (ponderados por effectiveness_score)
    top_hooks: list[dict]  # [{text, type, effectiveness, frequency}]
    optimal_structure: dict  # {hook_duration, intro_duration, sections, ...}
    effective_ctas: list[dict]  # [{text, position, frequency, type}]
    key_vocabulary: dict  # {technical_terms, transitions, common_phrases}
    notable_techniques: list[dict]  # [{name, description, frequency}]
    seo_patterns: dict  # {title_keywords, tags, ...}

    # Metadata
    average_effectiveness: float
    synthesis_timestamp: datetime

    # Report
    markdown_report: str  # Full synthesis report


@dataclass
class GeneratedScript:
    """Guión generado para YouTube"""

    user_idea: str

    # Guión
    script_markdown: str  # Guión completo con timestamps
    estimated_duration_minutes: int
    word_count: int

    # SEO
    seo_title: str
    seo_description: str
    seo_tags: list[str]

    # Metadata
    synthesis_used: str  # Topic de synthesis
    num_reference_videos: int
    generation_timestamp: datetime
    cost_usd: float

    # Quality estimate
    estimated_quality_score: int  # 1-100
