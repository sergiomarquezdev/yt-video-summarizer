# Audio Narration Processing in Vplay Project

This document details the audio processing workflow for videos classified as "Narración" (Narration) within the Vplay project. This flow is primarily handled by `src/detect_music.py`, which then utilizes `src/utils_narracion.py` for the actual audio-to-text transcription using OpenAI's Whisper model.

## Prerequisites

This process occurs *after* the video has been downloaded and converted to a `.wav` audio file (typically stored in `tmp/audio/`) by the `src/download_videos.py` module. The main entry point for this stage is the `run_music_detection(audio_path, conn)` function in `src/detect_music.py`, which is called from `src/listener.py`.

## Step 1: Voice and Music Detection (`src/detect_music.py` -> `run_music_detection`)

Before a video is confirmed as "Narración," the `run_music_detection` function performs initial analysis:

1.  **Detect Voice**: Calls `detect_voice(audio_path)`.
    *   This function uses the Silero VAD (Voice Activity Detection) model (`silero_vad.onnx` loaded via `utils_vad.py` from the `models/silero-vad/` directory).
    *   It loads the audio using `torchaudio.load()`, converts it to mono, and resamples to 16000 Hz if necessary (using `torchaudio.transforms.Resample`).
    *   `get_speech_timestamps()` is used to find segments of speech.
    *   Returns `has_voice` (boolean) based on whether speech segments were found above a certain `MUSIC_THRESHOLD` (this threshold name seems a bit confusing here, it's used for VAD).
2.  **Detect Music**: Calls `detect_music(audio_path)` (confusingly, this is a different function within the same file, perhaps it should be named `detect_music_presence` or similar to distinguish from the main orchestrator `run_music_detection`).
    *   This function uses the `demucs` command-line tool to separate audio sources (vocals, drums, bass, other).
    *   It calculates the average amplitude of non-vocal stems (drums, bass, other).
    *   Returns `has_music` (boolean) if this average amplitude is above `MUSIC_THRESHOLD` (defined in `config/settings.json`).
3.  **Update Database**: Calls `update_video_audio_analysis(filename, has_voice, has_music, conn)` (from `src/utils_db.py`).
    *   This function determines the `video_type` based on `has_voice` and `has_music`:
        *   Voice only: "Narración"
        *   Music only: "Instrumental"
        *   Voice and Music: "Mixto"
        *   Neither: "No_categorizable"
    *   It then updates the `videos` table in the database with `voice_detected`, `music_detected`, and `video_type` for the given video file.
4.  **Retrieve Video Info**: Calls `get_video_info(filename, conn)` (from `src/utils_db.py`) to fetch the `video_id` and the determined `video_type` from the database.

## Step 2: Handling the "Narración" Case (`src/detect_music.py` -> `run_music_detection`)

If `video_type` is determined to be "Narración":

1.  **Log Message**: Prints a message indicating that the video is narrative and transcription will begin using Whisper with the configured model (e.g., "medium").
    ```python
    # In src/detect_music.py, within run_music_detection
    if video_type == "Narración":
        print(f"Video narrativo: transcribiendo con Whisper ({WHISPER_MODEL})...")
        transcription, elapsed_time = transcribe_audio(audio_path)
    ```
2.  **Transcribe Audio**: Calls `transcribe_audio(audio_path)` function from `src/utils_narracion.py`.

## Step 3: Audio Transcription (`src/utils_narracion.py` -> `transcribe_audio`)

This function is responsible for converting the audio content to text:

1.  **Configuration**: It loads the Whisper model name (`WHISPER_MODEL`) and device (`WHISPER_DEVICE`) from `config/settings.json` (e.g., model: "medium", device: "cpu").
2.  **Load Model**: Loads the specified Whisper model using `whisper.load_model(model_name).to(device)`.
3.  **Perform Transcription**: Calls `model.transcribe(file_path)` on the provided `audio_path` (which is the `.wav` file).
4.  **Result**: The `transcribe` method returns a dictionary. The actual transcribed text is extracted from `result["text"]`.
5.  **Timing**: It measures the time taken for the transcription process.
6.  **Return Value**: Returns a tuple containing the `transcribed_text` (string) and `elapsed_time` (float).

## Step 4: Storing the Narration Transcript (`src/detect_music.py` -> `run_music_detection`)

Back in `src/detect_music.py`, after `transcribe_audio` returns:

1.  **Empty Transcription Check**: It checks if the returned `transcription` is empty or only whitespace.
    ```python
    if not transcription.strip():  # Si la transcripción está vacía
        print(f"Whisper no generó transcripción para {audio_path}. Se guardará '-' en la BD.")
        transcription = "-"
        elapsed_time = 0
    ```
    If empty, the `transcription` is set to `"-"`, and `elapsed_time` to `0`.
2.  **Update Database with Transcription**: Calls `update_transcripts_narracion(video_id, WHISPER_MODEL, elapsed_time, transcription, conn)` from `src/utils_db.py`.

## Step 5: Database Update for Narration Transcript (`src/utils_db.py` -> `update_transcripts_narracion`)

This function saves the transcription details to the `transcripts` table in the database:

1.  **SQL Operation**: It executes an `INSERT ... ON CONFLICT (video_id) DO UPDATE SET ...` SQL query. This means if a record for the `video_id` already exists in `transcripts`, it will be updated; otherwise, a new record will be inserted.
2.  **Data Stored**: The following fields are populated:
    *   `video_id`: The ID of the video.
    *   `transcript_model`: The name of the Whisper model used (e.g., "medium").
    *   `processing_time_transcription`: The `elapsed_time` taken by Whisper.
    *   `transcript_raw_audio`: The `transcription` text.
    *   `transcript_clean_audio`: The `transcription` text (same as raw for narration).
    *   `transcript_final`: The `transcription` text (same as raw for narration, this field is likely used later by `src/classify_categories.py`).
    *   `transcript_created_at`: Set to the current timestamp (`NOW()`).

## Summary of Narration Audio Processing

For a video identified as "Narración":

1.  The system determines there is voice but no significant music.
2.  The `.wav` audio file is passed to the Whisper model (configured via `settings.json`, e.g., "medium" model on CPU).
3.  Whisper transcribes the entire audio content into text.
4.  This transcribed text, along with the model name and processing time, is then stored in the `transcripts` table in the database. The same text is used for raw, clean, and final audio transcript fields for narration cases.

This transcribed text (`transcript_final`) is later retrieved by `src/classify_categories.py` to generate keywords and categories using GPT.

## Key Files and Configurations:

*   **Orchestration & Logic**: `src/detect_music.py`
*   **Transcription Utility**: `src/utils_narracion.py`
*   **Database Interactions**: `src/utils_db.py`
*   **Whisper Model Config**: `config/settings.json` (section `"transcription"`)
*   **VAD Model**: `models/silero-vad/silero_vad.onnx`
*   **Demucs**: Used for music detection (though less relevant if only narration is expected).

## Detailed Components for Narration Processing

This section expands on the key files, functions, and configurations specifically relevant to the "Narraci?n" audio processing path.

**1. Core Python Modules (`src/` directory):**

*   **`detect_music.py`** (Main orchestrator for this stage):
    *   `run_music_detection(audio_path, conn)`: The primary function that:
        *   Calls `detect_voice()` and `detect_music()` (the local Demucs-based one).
        *   Calls `update_video_audio_analysis()` to set `video_type` in the DB.
        *   Retrieves `video_id` and `video_type` using `get_video_info()`.
        *   If `video_type == "Narraci?n"`, it proceeds to call `transcribe_audio()`.
        *   Handles the result of transcription and calls `update_transcripts_narracion()`.
    *   `detect_voice(audio_path, threshold)`:
        *   Uses `torchaudio.load()` and `torchaudio.transforms.Resample`.
        *   Loads the Silero VAD model (`silero_vad.onnx` via `load_silero_vad()` from `silero_vad.model`).
        *   Uses `get_speech_timestamps()` (from `utils_vad`) for voice activity detection.
    *   `detect_music(audio_path, threshold)`: (Less critical for pure narration, but part of the initial analysis)
        *   Executes `demucs` as a subprocess to separate audio stems.
        *   Analyzes amplitudes of non-vocal stems.
*   **`utils_narracion.py`** (Whisper transcription):
    *   `transcribe_audio(file_path, model_name, device)`:
        *   Loads the specified Whisper model (e.g., "medium") using `whisper.load_model()`.
        *   Performs transcription using `model.transcribe()`.
        *   Returns the transcribed text (`result["text"]`) and processing time.
*   **`utils_db.py`** (Database interactions related to narration processing):
    *   `update_video_audio_analysis(filename, has_voice, has_music, conn)`: Sets `voice_detected`, `music_detected`, and `video_type` in the `videos` table.
    *   `get_video_info(filename, conn)`: Retrieves `video_id` and `video_type` from the `videos` table.
    *   `update_transcripts_narracion(video_id, model_name, processing_time, transcript_text, conn)`: Inserts/updates the narration transcript in the `transcripts` table, populating `transcript_raw_audio`, `transcript_clean_audio`, and `transcript_final` with the same Whisper output.

**2. Key Model Files (`models/` directory):**

*   **`models/silero-vad/silero_vad.onnx`**: The ONNX model file for Silero Voice Activity Detection.
*   **`models/silero-vad/utils_vad.py`**: Utility functions for the Silero VAD model, notably `get_speech_timestamps`.
*   **`models/clap-htsat-unfused/`**: (Not directly used in the pure "Narraci?n" path but loaded by `detect_music.py` for the "Mixto" case). Contains the CLAP model for audio classification.
*   **`models/demucs/`**: (Used by the `detect_music` function in `detect_music.py`). Configuration and environment for Demucs, which itself is installed via pip.
    *   Note: Whisper models specified in `config/settings.json` (e.g., "medium") are downloaded by the `whisper` library on first use to its cache, not typically pre-placed in the `models/` directory by a setup script unless explicitly managed that way.

**3. Configuration Files:**

*   **`config/settings.json`**:
    *   `"thresholds"`:
        *   `"voice"`: Threshold for Silero VAD (though the variable in `detect_voice` is named `threshold` and takes `MUSIC_THRESHOLD` as default in `detect_voice` call, which might be slightly confusing).
        *   `"music"`: Threshold for Demucs-based music detection.
    *   `"transcription"` section:
        *   `"model"`: Specifies the Whisper model to use (e.g., "medium").
        *   `"device"`: Specifies the device for Whisper (e.g., "cpu" or "cuda").

**4. External Tools & Libraries (Key Dependencies from `requirements.txt`):**

*   **`openai-whisper`**: The Python package for OpenAI's Whisper model.
*   **`torch`**, **`torchaudio`**: For audio loading, manipulation, and underlying tensor operations for models.
*   **`silero-vad`**: Python package for Silero VAD.
*   **`demucs`**: Python package for the Demucs music source separation tool.
*   **`psycopg2-binary`**: For PostgreSQL database connection.

This detailed breakdown should provide a clearer view of the components involved specifically when processing narration-only audio.
