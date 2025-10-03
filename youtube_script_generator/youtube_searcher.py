"""YouTube Searcher - Finds and ranks videos using yt-dlp."""

import logging
import subprocess

from youtube_script_generator.models import YouTubeVideo


logger = logging.getLogger(__name__)


class YouTubeSearchError(Exception):
    """Raised when YouTube search fails."""

    pass


class YouTubeSearcher:
    """Searches YouTube and ranks videos by quality metrics."""

    def __init__(self, max_results: int = 10):
        """Initialize the YouTube searcher.

        Args:
            max_results: Maximum number of videos to return
        """
        self.max_results = max_results

    def search(
        self,
        query: str,
        duration_preference: int | None = None,
        min_duration: int = 5,
        max_duration: int = 45,
    ) -> list[YouTubeVideo]:
        """Search YouTube and return ranked videos.

        Args:
            query: Optimized search query
            duration_preference: Preferred video duration in minutes (optional)
            min_duration: Minimum video duration in minutes
            max_duration: Maximum video duration in minutes

        Returns:
            List of YouTubeVideo objects sorted by quality_score

        Raises:
            YouTubeSearchError: If search fails
        """
        logger.info(f"Searching YouTube for: {query}")

        try:
            # Build yt-dlp command for YouTube search
            # We search for more than max_results to account for filtering
            search_count = self.max_results * 3

            cmd = [
                "yt-dlp",
                f"ytsearch{search_count}:{query}",
                "--dump-json",
                "--no-warnings",
                "--no-playlist",
                "--skip-download",
            ]

            # Execute search
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=True,
            )

            # Parse results
            videos = self._parse_search_results(
                result.stdout,
                min_duration,
                max_duration,
            )

            if not videos:
                raise YouTubeSearchError(f"No videos found for query: {query}")

            # Calculate quality scores with duration preference
            for video in videos:
                video.duration_preference = duration_preference

            # Sort by quality score (descending)
            videos.sort(key=lambda v: v.quality_score, reverse=True)

            # Return top N
            final_videos = videos[: self.max_results]
            logger.info(f"Found {len(final_videos)} videos matching criteria")

            return final_videos

        except subprocess.TimeoutExpired as e:
            raise YouTubeSearchError("YouTube search timed out") from e
        except subprocess.CalledProcessError as e:
            raise YouTubeSearchError(f"YouTube search failed: {e.stderr}") from e
        except Exception as e:
            raise YouTubeSearchError(f"Unexpected error during search: {e}") from e

    def _parse_search_results(
        self,
        json_output: str,
        min_duration: int,
        max_duration: int,
    ) -> list[YouTubeVideo]:
        """Parse yt-dlp JSON output into YouTubeVideo objects.

        Args:
            json_output: Raw JSON output from yt-dlp
            min_duration: Minimum duration in minutes
            max_duration: Maximum duration in minutes

        Returns:
            List of YouTubeVideo objects that meet duration criteria
        """
        import json

        videos = []
        min_seconds = min_duration * 60
        max_seconds = max_duration * 60

        for line in json_output.strip().split("\n"):
            if not line:
                continue

            try:
                data = json.loads(line)

                # Extract duration
                duration = data.get("duration")
                if not duration:
                    continue

                # Filter by duration
                if duration < min_seconds or duration > max_seconds:
                    continue

                # Extract metadata
                video = YouTubeVideo(
                    video_id=data.get("id", ""),
                    title=data.get("title", "Unknown"),
                    url=data.get("webpage_url", data.get("url", "")),
                    duration_seconds=duration,
                    view_count=data.get("view_count", 0),
                    upload_date=data.get("upload_date", ""),
                    channel=data.get("uploader", data.get("channel", "Unknown")),
                    like_count=data.get("like_count"),
                )

                videos.append(video)

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse video data: {e}")
                continue

        return videos
