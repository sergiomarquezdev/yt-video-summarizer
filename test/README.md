# Test Directory Structure

This directory contains all tests for the YouTube Transcriber project.

## Structure

```
test/
├── conftest.py              # Shared fixtures and pytest configuration
├── test_infrastructure.py   # Infrastructure sanity checks
├── test_config.py          # Tests for config.py (to be created)
├── test_utils.py           # Tests for utils.py (to be created)
├── test_downloader.py      # Tests for downloader.py (to be created)
├── test_transcriber.py     # Tests for transcriber.py (to be created)
└── test_cli.py             # Integration tests for CLI (to be created)
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_config.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=yt_transcriber --cov-report=html

# Run tests by marker
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m slow          # Only slow tests

# Run specific test
pytest test/test_config.py::TestAppSettings::test_default_values
```

## Test Markers

- `@pytest.mark.unit`: Fast unit tests with no external dependencies
- `@pytest.mark.integration`: Integration tests that may use external services
- `@pytest.mark.slow`: Tests that take several seconds to run
- `@pytest.mark.cuda`: Tests requiring CUDA/GPU
- `@pytest.mark.cpu`: Tests for CPU-only execution

## Fixtures

See `conftest.py` for all available fixtures.

### Common Fixtures

- `temp_test_dir`: Temporary directory for test files
- `temp_output_dir`: Temporary directory for output files
- `sample_youtube_url`: Sample YouTube URL
- `sample_video_info`: Mock video info from yt-dlp
- `sample_transcription_result`: Mock transcription result from Whisper
- `mock_ytdl`: Mocked yt-dlp instance
- `mock_whisper_model`: Mocked Whisper model
- `mock_cuda_available`/`mock_cuda_unavailable`: Mock CUDA availability

## Writing Tests

### TDD Workflow

1. **RED**: Write a failing test that defines expected behavior
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve code quality while keeping tests green

### Example Test

```python
import pytest
from yt_transcriber import utils


class TestFilenameNormalization:
    """Tests for filename normalization function."""

    def test_removes_special_characters(self):
        """Test that special characters are removed."""
        result = utils.normalize_title_for_filename("Test/Video:Name")
        assert "/" not in result
        assert ":" not in result

    @pytest.mark.parametrize("input,expected", [
        ("normal title", "normal_title"),
        ("Title With Spaces", "Title_With_Spaces"),
        ("", "untitled"),
    ])
    def test_various_inputs(self, input, expected):
        """Test various input scenarios."""
        result = utils.normalize_title_for_filename(input)
        assert result == expected
```

## Coverage

Target coverage: **>80%** for core modules

Check coverage report:

```bash
pytest --cov=yt_transcriber --cov-report=html
# Open htmlcov/index.html in browser
```

## Notes

- Mock all external dependencies (yt-dlp, Whisper, filesystem)
- Use `tmp_path` fixture for file operations
- Tests should be independent and order-agnostic
- Clean up resources in fixtures or use context managers
