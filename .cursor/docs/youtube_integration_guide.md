# Guide: Integrating YouTube Video Downloads

This document provides a step-by-step guide on how to modify the existing Vplay project to support video downloads from YouTube, in addition to the current Vimeo functionality. The primary tool for this will be `yt-dlp`, which is already listed as a dependency in `requirements.txt`.

## 1. Rationale for using `yt-dlp`

`yt-dlp` is a powerful and actively maintained command-line program and Python library to download videos from YouTube and many other sites. Its advantages include:

*   **Broad Site Support**: While we focus on YouTube, its versatility is a plus.
*   **Rich Metadata Extraction**: Can provide extensive information about videos (title, uploader, duration, description, formats, etc.).
*   **Format Selection**: Allows detailed control over the video and audio formats to download.
*   **Python Library**: Can be imported and used directly in Python, allowing for cleaner integration than calling it as a subprocess for metadata extraction and download control.

## 2. Core Module for Modification: `src/download_videos.py`

This file will require the most significant changes. The strategy involves:

1.  Detecting the video source (Vimeo or YouTube) from the URL.
2.  Dispatching to a source-specific download function.
3.  Normalizing the metadata obtained from YouTube to fit the existing database structure.

### 2.1. Modifying `run_download_pipeline` for Source Detection

This function will act as a dispatcher.

```python
# In src/download_videos.py
# ... (import yt_dlp at the top of the file: import yt_dlp)
# ... (import datetime if not already there: from datetime import datetime)
# ... (ensure os is imported: import os)

def run_download_pipeline(pubsub_data: Dict[str, str], conn, operation: str) -> Optional[str]:
    title = pubsub_data.get("title")
    url = pubsub_data.get("url")
    author = pubsub_data.get("author", "Desconocido")
    description = pubsub_data.get("description", "")

    print(f"\n🚀 Procesando entrada de Pub/Sub: {title} - {url}\n")
    if not title or not url:
        print("❌ Error: Título o URL faltante.")
        # Consider using a structured error from utils_error.py
        return None

    print(f"📨 Título desde Pub/Sub recibido: '{title}'")
    video_result_path = None

    if "youtube.com" in url or "youtu.be" in url:
        print("🐍 Detectada URL de YouTube. Iniciando descarga con yt-dlp...")
        video_result_path = download_youtube_video(url, RAW_VIDEOS_DIR, pubsub_data, operation, conn)
    elif "vimeo.com" in url:
        print("🎥 Detectada URL de Vimeo. Iniciando descarga con API de Vimeo...")
        # Consider renaming the original download_video to download_vimeo_video for clarity
        video_result_path = download_vimeo_video(url, RAW_VIDEOS_DIR, description, author, operation, title, conn)
    else:
        print(f"❌ URL no soportada: {url}")
        # Use a structured error from src.utils_error for consistency
        # publish_response(error_pipeline_failed(url=url, details="URL de video no soportada."))
        return None # Or an error dictionary

    if isinstance(video_result_path, dict) and video_result_path.get("status") == "error":
        # Error dictionary already formatted, can be returned directly to listener
        return video_result_path

    if video_result_path and os.path.exists(video_result_path):
        audio_path = convert_video_to_audio(video_result_path, AUDIO_DIR, conn)
        print("✅ Video procesado y convertido a audio correctamente.")
        return audio_path
    else:
        print("❌ No se pudo descargar o encontrar el video.")
        # Use a structured error from src.utils_error
        return None # Or an error dictionary
```

### 2.2. New Function: `download_youtube_video`

This function will use the `yt-dlp` Python library.

```python
# In src/download_videos.py

# Make sure to import at the top of the file:
# import yt_dlp
# import os
# from datetime import datetime
# from .utils_db import insert_video_metadata # Assuming relative import or correct sys.path
# from .utils_error import error_pipeline_failed # For structured errors

def download_youtube_video(video_url: str, download_folder: str, pubsub_data: dict, operation: str, conn) -> Optional[str]:
    video_title_pubsub = pubsub_data.get("title", "Video sin título")
    description_pubsub = pubsub_data.get("description", "")
    author_pubsub = pubsub_data.get("author", "Desconocido")

    # Ensure download_folder exists
    os.makedirs(download_folder, exist_ok=True)

    # yt-dlp options
    # We want to control the filename to match the existing pattern if possible,
    # or use a sanitized version of the Pub/Sub title.
    # For now, let's use a sanitized version of pubsub_title as the base filename.
    base_filename = sanitize_filename(video_title_pubsub)
    output_template = os.path.join(download_folder, f"{base_filename}.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', # Download best MP4, or best overall if MP4 not available
        'outtmpl': output_template,
        'quiet': True,
        'noplaylist': True, # Ensures only single video is downloaded if URL is part of playlist
        # 'writesanitized': True, # yt-dlp can sanitize, but we defined output_template
    }

    downloaded_filepath = None
    video_actual_extension = "mp4" # Default assumption

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False) # First, get info without downloading

            # Determine the actual extension and construct the final filename before download
            video_actual_extension = info_dict.get('ext', 'mp4')
            final_filename_with_ext = f"{base_filename}.{video_actual_extension}"
            downloaded_filepath = os.path.join(download_folder, final_filename_with_ext)

            # Update ydl_opts to use the exact filename, then download
            ydl.params['outtmpl'] = downloaded_filepath
            ydl.download([video_url])

            print(f"✅ Descarga de YouTube completada: {downloaded_filepath}")

            # Ensure file exists after download call, yt-dlp can sometimes be tricky
            if not os.path.exists(downloaded_filepath):
                 print(f"❌ Error: yt-dlp reported download but file not found at {downloaded_filepath}")
                 # Fallback: try to find file if extension was guessed wrong, though less likely with extract_info first
                 # This part might need robust globbing if filename from yt-dlp is unpredictable
                 possible_files = [f for f in os.listdir(download_folder) if f.startswith(base_filename)]
                 if possible_files:
                    downloaded_filepath = os.path.join(download_folder, possible_files[0])
                    print(f"Found file via fallback: {downloaded_filepath}")
                 else:
                    return error_pipeline_failed(url=video_url, details="Archivo no encontrado tras descarga de yt-dlp.")

            metadata = {
                "video_filename": final_filename_with_ext, # Use the constructed filename
                "url": video_url,
                "video_size_MB": round(os.path.getsize(downloaded_filepath) / (1024 * 1024), 2),
                "video_title": video_title_pubsub, # Consistent with Vimeo flow
                "video_description": description_pubsub,
                "video_author": info_dict.get('uploader', author_pubsub), # Prefer yt-dlp's uploader if available
                "video_duration_seconds": round(float(info_dict.get("duration", 0)), 2),
                "processing_datetime": datetime.now(),
                "processing_time_video_to_audio": None # To be filled by convert_video_to_audio
            }

            print(f"📄 Insertando metadatos de YouTube en base de datos...")
            # Ensure insert_video_metadata is correctly imported and conn is passed
            from .utils_db import insert_video_metadata
            insert_result = insert_video_metadata(metadata, operation, conn)
            if isinstance(insert_result, dict) and insert_result.get("status") == "error":
                return insert_result # Propagate error dictionary

            return downloaded_filepath

    except yt_dlp.utils.DownloadError as e:
        print(f"❌ Error de yt-dlp durante la descarga de '{video_url}': {e}")
        return error_pipeline_failed(url=video_url, details=f"yt-dlp DownloadError: {e}")
    except Exception as e:
        print(f"❌ Error inesperado durante la descarga de YouTube '{video_url}': {e}")
        return error_pipeline_failed(url=video_url, details=f"Error inesperado: {e}")
```

### 2.3. Refactor `download_video` to `download_vimeo_video`

The existing `download_video` function should be renamed to `download_vimeo_video` for clarity. Its internal logic for interacting with the Vimeo API remains the same. Make sure to update the call site in the modified `run_download_pipeline`.

```python
# In src/download_videos.py

def download_vimeo_video(url: str, folder: str, description: str, author: str, operation: str, pubsub_title: str, conn):
    # ... (current implementation of download_video, ensure conn is passed to insert_video_metadata)
    # Make sure insert_video_metadata(metadata, operation, conn) is called within this function.
    pass # Placeholder for actual refactored code
```

### 2.4. Helper `sanitize_filename`

This function is already present and can be reused for the YouTube filenames if constructing them manually or as a part of the `output_template` for `yt-dlp` if needed, though `yt-dlp` often handles sanitization well with its template system.

## 3. Database Considerations (`src/utils_db.py`)

*   **`insert_video_metadata(metadata, operation, conn)`**: This function should largely remain compatible. The key is that the `metadata` dictionary passed from `download_youtube_video` must contain the same keys (e.g., `video_filename`, `video_title`, `video_duration_seconds`, etc.) that the function expects and that are currently provided by the Vimeo download process.
    *   A small adjustment: ensure `conn` is a parameter in `insert_video_metadata` if it wasn't explicitly before, and that it's used for all DB operations within that function.

## 4. Environment Variables

No new environment variables are strictly necessary for `yt-dlp` to function for public YouTube videos.

## 5. Key Challenges and Considerations

*   **Metadata Mapping**: `yt-dlp`'s `info_dict` is very rich. Carefully map its fields (like `title`, `uploader`, `channel`, `duration`, `description`) to your existing database schema and the expectations of `insert_video_metadata`.
*   **Filename Consistency**: Decide on a consistent filename strategy. Using `pubsub_data.get("title")` as the base for `video_filename` (after sanitization) seems to be the current project's approach for `video_title` in DB, while the actual file saved might be different. For YouTube, `yt-dlp` can create filenames based on the video's actual YouTube title. Ensure `video_filename` stored in the DB is the one you expect for lookups.
*   **Error Handling**: `yt-dlp` can raise specific exceptions (like `yt_dlp.utils.DownloadError`). Catch these and translate them into your project's error reporting structure (e.g., using functions from `src/utils_error.py` to publish to Pub/Sub).
*   **Testing**: Thoroughly test with various YouTube URL formats (short links, links with playlists, direct video links, etc.) and different types of videos.
*   **`convert_video_to_audio`**: This function should workfine as long as `yt-dlp` downloads a compatible video format (like MP4) that `ffmpeg` can process.

## 6. Installation of `yt-dlp`

`yt-dlp` is already in `requirements.txt`, so it should be installed when setting up the environment or building the Docker image.

## Conclusion

Integrating YouTube downloads is feasible and significantly aided by `yt-dlp`. The main effort lies in the careful integration into the existing workflow in `src/download_videos.py`, robust metadata handling, and consistent error reporting. By creating a dispatching mechanism and a dedicated YouTube download function, the system can be made more extensible for other video sources in the future.

## Implementation Checklist

Here is a checklist of tasks to ensure a complete integration of YouTube video downloads:

1.  **Modify `src/download_videos.py`:**
    *   [ ] Add `import yt_dlp` and any other necessary imports (e.g., `datetime`).
    *   [ ] Implement the `download_youtube_video` function as detailed in section 2.2, paying close attention to:
        *   [ ] Correct `ydl_opts` for format and output template.
        *   [ ] Robust extraction of `info_dict` and mapping to `metadata` dictionary.
        *   [ ] Consistent filename generation (`final_filename_with_ext`).
        *   [ ] Correct call to `insert_video_metadata` with `conn` and `operation`.
        *   [ ] Comprehensive error handling for `yt_dlp.utils.DownloadError` and other exceptions, returning structured errors.
    *   [ ] Refactor the existing `download_video` function to `download_vimeo_video` (section 2.3).
        *   [ ] Ensure it correctly passes `conn` to `insert_video_metadata`.
    *   [ ] Update `run_download_pipeline` (section 2.1) to:
        *   [ ] Include logic to detect YouTube URLs (`youtube.com`, `youtu.be`).
        *   [ ] Call `download_youtube_video` for YouTube links.
        *   [ ] Call the refactored `download_vimeo_video` for Vimeo links.
        *   [ ] Handle unsupported URLs gracefully (e.g., return a structured error).
2.  **Verify `src/utils_db.py`:**
    *   [ ] Ensure `insert_video_metadata(metadata, operation, conn)` function:
        *   [ ] Accepts `conn` as a parameter.
        *   [ ] Is compatible with the `metadata` structure provided by `download_youtube_video`.
        *   [ ] Correctly handles `operation` for both create and update scenarios if applicable.
3.  **Verify `src/utils_error.py`:**
    *   [ ] Ensure that `error_pipeline_failed` or similar functions can be used to create structured error messages for YouTube download failures, suitable for `publish_response`.
4.  **Dependencies:**
    *   [ ] Confirm `yt-dlp` is in `requirements.txt` (already done).
    *   [ ] Rebuild Docker image if necessary to include any changes or new dependencies if they were added (though `yt-dlp` should already be there).
5.  **Testing:**
    *   [ ] Test with various valid YouTube video URLs (standard, short, with playlists - ensuring only single video downloads).
    *   [ ] Test with invalid or private YouTube video URLs to check error handling.
    *   [ ] Test with Vimeo URLs to ensure existing functionality is not broken.
    *   [ ] Verify that metadata (title, author, duration, etc.) is correctly extracted and stored for YouTube videos.
    *   [ ] Verify that the downloaded YouTube video is correctly converted to audio by `convert_video_to_audio`.
    *   [ ] Verify that the entire pipeline (download, audio conversion, transcription, classification) works for YouTube videos.
6.  **Configuration (`config/settings.json`):**
    *   [ ] Review if any new configuration specific to YouTube (e.g., preferred quality, API keys if ever needed for private videos - though not for public) might be useful in the future. For now, no changes seem immediately necessary based on the proposed `yt-dlp` library usage for public videos.
7.  **Documentation:**
    *   [ ] Update any relevant internal or external documentation to reflect the new YouTube download capability.
    *   [ ] This guide (`youtube_integration_guide.md`) can serve as the primary reference.
