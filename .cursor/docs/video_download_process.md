# Video Download Process in Vplay Project

This document outlines the step-by-step process of how videos are downloaded and initially processed within the Vplay project. The process starts when a message is received by `listener.py` via Google Cloud Pub/Sub.

## Step 1: Message Reception (`src/listener.py`)

1.  **Pub/Sub Listener**: The `start_listener()` function in `src/listener.py` initializes a Pub/Sub subscriber client. It listens for messages on the `INPUT_SUBSCRIPTION_ID` specified in `config/settings.json` (under `pubsub` section).
2.  **Callback Execution**: When a message arrives, the `callback(message)` function is triggered.
    *   The message data is decoded from UTF-8 and parsed as JSON.
    *   The `operation` field in the Pub/Sub data (e.g., "create", "modify", "delete") is converted to lowercase.
    *   Key data expected from the Pub/Sub message typically includes:
        *   `url`: The Vimeo URL of the video.
        *   `title`: The title to be used for the video in the system.
        *   `author`: The author of the video.
        *   `description`: A description of the video.
        *   `operation`: The action to perform (create, modify, delete).
3.  **Pipeline Initiation**: The `callback` function then calls `run_pipeline(pubsub_data, operation)`, passing the parsed message data and the operation type.

## Step 2: Pipeline Orchestration (`src/listener.py` -> `run_pipeline`)

The `run_pipeline` function in `src/listener.py` orchestrates the main processing flow:

1.  **Data Validation**: It first checks if all required fields (`title`, `url`, `author`, `description`, `operation`) are present in the `pubsub_data`. If not, an error response is published.
2.  **Database Connection**: It establishes a connection to the PostgreSQL database using `connect_db()` from `src/utils_db.py`. It includes a retry mechanism if the initial connection fails.
3.  **Download and Convert**: It calls the `download_videos` function (which is an alias for `run_download_pipeline` from `src/download_videos.py`), passing the `pubsub_data`, the database `conn`ection, and the `operation`.
    ```python
    # In listener.py
    download_result = download_videos(pubsub_data, conn, operation)
    audio_path = download_result
    ```
    If `download_result` indicates an error or if `audio_path` is not returned, the pipeline is aborted, and an error response is published.

## Step 3: Video Download and Initial Processing (`src/download_videos.py` -> `run_download_pipeline`)

The `run_download_pipeline` function in `src/download_videos.py` handles the download and initial conversion:

1.  **Extract Pub/Sub Data**: It extracts `title`, `url`, `author`, and `description` from the `pubsub_data` dictionary.
2.  **Call Core Download Function**: It then calls the `download_video` function, providing the extracted details. Crucially, `pubsub_title` (the title from Pub/Sub) is passed as the `video_title` to be stored in the database, while Vimeo's video name is used for the actual filename.
    ```python
    # In src/download_videos.py
    video_result = download_video(
        url=url,
        folder=RAW_VIDEOS_DIR, # Typically tmp/video/
        description=description,
        author=author,
        operation=operation,
        pubsub_title=title
    )
    ```
3.  **Error Handling**: If `download_video` returns an error (e.g., video already exists and operation is 'create'), this error is propagated up.
4.  **Video to Audio Conversion**: If `download_video` is successful and returns a `video_path`, `run_download_pipeline` then calls `convert_video_to_audio(video_result, AUDIO_DIR, conn)`.

## Step 4: Core Video Download Logic (`src/download_videos.py` -> `download_video`)

The `download_video` function is where the actual interaction with Vimeo and file download occurs:

1.  **Vimeo API Interaction**:
    *   It constructs the Vimeo API URL: `https://api.vimeo.com/videos/{video_id}`. The `video_id` is extracted from the input `url` using `get_video_id()`.
    *   It makes a GET request to this API endpoint using `requests.get()`. The request includes an `Authorization` header with a Bearer token (`ACCESS_TOKEN`), which is loaded from the `VIMEO_ACCESS_TOKEN` environment variable (defined in `.env`).
2.  **Fetch Video Information**:
    *   The API response (JSON) contains video metadata, including `name` (Vimeo's title for the video) and `download` (an array of download links for different qualities/formats).
    *   It checks if download links are available.
    *   It selects the best available download link, usually by picking the one with the maximum `width`.
3.  **Filename and Path**:
    *   The filename for the downloaded video is derived from `data.get('name', 'video_descargado')` (the name from Vimeo) and sanitized using `sanitize_filename()` to remove invalid characters and replace spaces with underscores. An `.mp4` extension is added.
    *   The video is saved to the `folder` argument, which is `RAW_VIDEOS_DIR` (defined as `BASE_DIR/tmp/video/`).
4.  **File Download**:
    *   The video content is downloaded from the selected `download_link` using `requests.get(download_link, stream=True)` and written to the local file path in chunks.
5.  **Metadata Collection**: After a successful download, it gathers metadata:
    *   `video_filename`: The sanitized filename.
    *   `url`: The original Vimeo URL.
    *   `video_size_MB`: Size of the downloaded file.
    *   `video_title`: The `pubsub_title` received from the Pub/Sub message.
    *   `video_description`, `video_author`: From Pub/Sub data.
    *   `video_duration_seconds`: From the Vimeo API response.
    *   `processing_datetime`: Current timestamp.
6.  **Database Insertion**: It calls `insert_video_metadata(metadata, operation)` (from `src/utils_db.py`) to record this information in the `videos` table in the database.

## Step 5: Database Update - Video Metadata (`src/utils_db.py` -> `insert_video_metadata`)

The `insert_video_metadata` function in `src/utils_db.py` handles the database interaction for the `videos` table:

1.  **Operation Handling**:
    *   **`create`**: Inserts a new record into the `videos` table. If a video with the same `filename` already exists (due to `UNIQUE` constraint on `filename`), it returns a `VIDEO_ID_EXISTS` error.
    *   **`modify`**: Updates an existing record in the `videos` table identified by `filename`. If the video doesn't exist, it returns a `VIDEO_ID_TO_MODIFY_NOT_FOUND` error.
    *   **`delete`**: Deletes the video record from `videos` and also cascades deletes to related tables (`video_keywords`, `video_categories`, `transcripts`). If the video doesn't exist, it returns `VIDEO_ID_TO_DELETE_NOT_FOUND` error. For a 'delete' operation that's successful, it returns a `PIPELINE_ABORTED_BY_DELETION` message, effectively stopping further processing for that video.
2.  **Data Stored**: Includes filename, URL, size, title, description, author, duration, and creation/update timestamps.

## Step 6: Video to Audio Conversion (`src/download_videos.py` -> `convert_video_to_audio`)

If the video download was successful, `run_download_pipeline` proceeds to convert the video to audio:

1.  **Path Setup**:
    *   Determines the input `video_path` and output `audio_path`. The audio filename is the same as the video's base name but with a `.wav` extension.
    *   Audio files are saved in `AUDIO_DIR` (defined as `BASE_DIR/tmp/audio/`).
2.  **FFmpeg Execution**:
    *   It uses `subprocess.run()` to execute `ffmpeg`.
    *   The `ffmpeg` command converts the input video to a WAV audio file with specific parameters:
        *   `-ac 1`: Mono audio (single channel).
        *   `-ar 16000`: Sample rate of 16000 Hz.
        *   `-y`: Overwrite output file if it exists.
        *   `-v warning`: Sets ffmpeg log level to warning.
3.  **Timing and DB Update**:
    *   It measures the time taken for the conversion.
    *   Calls `update_video_audio_processing(video_filename, elapsed_time, conn)` (from `src/utils_db.py`) to store this `elapsed_time` in the `videos` table for the corresponding video record.
4.  **Return Value**: Returns the `audio_path` if successful, otherwise `None`.

## Step 7: Database Update - Audio Processing Time (`src/utils_db.py` -> `update_video_audio_processing`)

This function simply updates the `processing_time_video_to_audio` field in the `videos` table for the given `filename`.

## Key Configurations and Environment Variables

*   **`VIMEO_ACCESS_TOKEN`**: Environment variable (in `.env`) required for Vimeo API access.
*   **Database Credentials**: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_SSLMODE` environment variables (in `.env`) for PostgreSQL connection.
*   **File Paths**:
    *   Downloaded videos: `tmp/video/` (relative to project root).
    *   Converted audio: `tmp/audio/` (relative to project root).
    *   These are primarily defined in `src/download_videos.py`.
*   **Pub/Sub Configuration**: `PROJECT_ID`, `INPUT_SUBSCRIPTION_ID` in `config/settings.json`.

## Conclusion

The video download process is a multi-step operation initiated by a Pub/Sub message. It involves fetching data from the Vimeo API, downloading the video file, storing metadata in a PostgreSQL database, and converting the video to a standardized WAV audio format for further analysis. Error handling is present at various stages to manage issues like duplicate videos, API errors, or missing files.

## Key Files, Functions, and Configurations

This section summarizes the most relevant components for the video download and initial conversion process:

**1. Core Python Modules (`src/` directory):**

*   **`listener.py`**:
    *   `start_listener()`: Initializes the Pub/Sub listener.
    *   `callback(message)`: Handles incoming Pub/Sub messages.
    *   `run_pipeline(pubsub_data, operation)`: Orchestrates the overall processing for a video, including calling the download module.
*   **`download_videos.py`**:
    *   `run_download_pipeline(pubsub_data, conn, operation)`: Main orchestrator for this module. Receives Pub/Sub data, calls `download_video` and then `convert_video_to_audio`.
    *   `download_video(url, folder, description, author, operation, pubsub_title)`: Handles the direct interaction with the Vimeo API, downloads the .mp4 file, and prepares metadata.
    *   `convert_video_to_audio(video_path, audio_dir, conn)`: Uses `ffmpeg` to convert the downloaded video to a `.wav` audio file.
    *   `get_video_id(video_url)`: Helper to extract video ID from a Vimeo URL.
    *   `sanitize_filename(name)`: Helper to clean filenames.
*   **`utils_db.py`**:
    *   `connect_db()`: Establishes the database connection.
    *   `insert_video_metadata(metadata, operation)`: Inserts or updates video metadata in the `videos` table (handles `create`, `modify`, `delete`).
    *   `update_video_audio_processing(filename, processing_time, conn)`: Updates the `videos` table with the time taken for video-to-audio conversion.
*   **`utils_error.py`**:
    *   Contains various `format_error()` and specific error functions (e.g., `error_video_id_exists()`, `error_pipeline_failed()`) used to structure error responses published back to Pub/Sub.

**2. Configuration Files:**

*   **`.env`** (in the project root):
    *   `VIMEO_ACCESS_TOKEN`: Essential for authenticating with the Vimeo API.
    *   `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_SSLMODE`: Credentials and connection parameters for the PostgreSQL database.
*   **`config/settings.json`**:
    *   `"pubsub"` section: Contains `PROJECT_ID` and `INPUT_SUBSCRIPTION_ID` which `listener.py` uses to listen for messages.
    *   `"paths"` section: Defines base paths for temporary data storage, although `src/download_videos.py` often re-defines `RAW_VIDEOS_DIR` and `AUDIO_DIR` relative to its own `BASE_DIR`.

**3. Key Directory Structure (relative to project root):**

*   `src/`: Contains all the core Python logic.
*   `tmp/video/`: Default directory where raw `.mp4` videos are downloaded.
*   `tmp/audio/`: Default directory where converted `.wav` files are stored.
*   `config/`: Contains `settings.json`.

**4. External Tools:**

*   **`ffmpeg`**: Command-line tool, essential for the `convert_video_to_audio` step. Its availability is assumed in the environment where the script/Docker container runs (installed in `Dockerfile`).

This overview should help in navigating the codebase related to the video download and initial conversion stages.
