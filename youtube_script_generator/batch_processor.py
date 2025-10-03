"""Batch Processor - Downloads and transcribes multiple videos in parallel."""

import logging
from pathlib import Path

import whisper
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

from youtube_script_generator.models import VideoTranscript, YouTubeVideo
from yt_transcriber.config import settings
from yt_transcriber.downloader import download_and_extract_audio
from yt_transcriber.transcriber import transcribe_audio_file


logger = logging.getLogger(__name__)
console = Console()


class BatchProcessingError(Exception):
    """Raised when batch processing fails."""

    pass


class BatchProcessor:
    """Processes multiple YouTube videos in parallel."""

    def __init__(
        self,
        temp_dir: Path | None = None,
        max_workers: int = 3,
        model_name: str | None = None,
    ):
        """Initialize the batch processor.

        Args:
            temp_dir: Temporary directory for downloads
            max_workers: Maximum parallel workers (not currently used - sequential processing)
            model_name: Whisper model name (defaults to config setting)
        """
        self.temp_dir = temp_dir or settings.TEMP_BATCH_DIR
        self.max_workers = max_workers
        self.model_name = model_name or settings.WHISPER_MODEL_NAME

        # Create temp directory if it doesn't exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Load Whisper model once for reuse
        logger.info(f"Loading Whisper model: {self.model_name}")
        self.whisper_model = whisper.load_model(self.model_name, device=settings.WHISPER_DEVICE)
        logger.info("Whisper model loaded successfully")

    def process_videos(
        self,
        videos: list[YouTubeVideo],
    ) -> list[VideoTranscript]:
        """Download and transcribe multiple videos.

        Args:
            videos: List of YouTubeVideo objects to process

        Returns:
            List of VideoTranscript objects

        Raises:
            BatchProcessingError: If processing fails for all videos
        """
        logger.info(f"Processing {len(videos)} videos...")
        transcripts = []
        failed_count = 0

        # Create progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Processing videos...", total=len(videos))

            for i, video in enumerate(videos, 1):
                try:
                    progress.update(
                        task,
                        description=f"[cyan]Processing {i}/{len(videos)}: {video.title[:50]}...",
                    )

                    # Download video
                    audio_path = self._download_video(video)

                    # Transcribe video
                    transcript = self._transcribe_video(audio_path, video)
                    transcripts.append(transcript)

                    # Cleanup audio file
                    audio_path.unlink(missing_ok=True)

                    logger.info(f"✓ Successfully processed: {video.title}")

                except Exception as e:
                    logger.error(f"✗ Failed to process {video.title}: {e}")
                    failed_count += 1

                finally:
                    progress.advance(task)

        # Cleanup temp directory
        self._cleanup()

        if not transcripts:
            raise BatchProcessingError(f"Failed to process all {len(videos)} videos")

        success_rate = (len(transcripts) / len(videos)) * 100
        logger.info(
            f"Batch processing complete: {len(transcripts)}/{len(videos)} "
            f"succeeded ({success_rate:.1f}%)"
        )

        return transcripts

    def _download_video(self, video: YouTubeVideo) -> Path:
        """Download a single video.

        Args:
            video: YouTubeVideo to download

        Returns:
            Path to downloaded audio file

        Raises:
            Exception: If download fails
        """
        import uuid

        logger.debug(f"Downloading: {video.url}")

        # Generate unique job ID for this download
        job_id = str(uuid.uuid4())[:8]

        # Use existing downloader from yt_transcriber
        result = download_and_extract_audio(
            youtube_url=video.url, temp_dir=self.temp_dir, unique_job_id=job_id
        )

        return result.audio_path

    def _transcribe_video(self, audio_path: Path, video: YouTubeVideo) -> VideoTranscript:
        """Transcribe a single video.

        Args:
            audio_path: Path to audio file
            video: Original YouTubeVideo object

        Returns:
            VideoTranscript object

        Raises:
            Exception: If transcription fails
        """
        import time

        logger.debug(f"Transcribing: {audio_path.name}")

        start_time = time.time()

        # Use existing transcriber from yt_transcriber
        result = transcribe_audio_file(
            audio_path=audio_path,
            model=self.whisper_model,  # Pass the loaded model
        )

        transcription_time = time.time() - start_time

        # Note: TranscriptionResult only has .text and .language
        # We'll store empty list for word_timestamps since the current
        # transcriber doesn't return them
        return VideoTranscript(
            video=video,
            transcript_text=result.text,
            word_timestamps=[],  # Not available from current transcriber
            language=result.language or "unknown",
            transcription_time_seconds=transcription_time,
        )

    def _cleanup(self):
        """Clean up temporary files."""
        try:
            if self.temp_dir.exists():
                # Remove all files in temp directory
                for item in self.temp_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                logger.debug(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")
