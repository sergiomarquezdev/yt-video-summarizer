# Category and Keyword Classification Process in Vplay Project

This document explains how transcribed video content is processed by `src/classify_categories.py` to generate relevant keywords and assign categories using Azure OpenAI (GPT models). This is typically one of the final steps in the video analysis pipeline.

## Prerequisites

This process assumes:
1.  The video has been downloaded and converted to audio.
2.  The audio has been processed by `src/detect_music.py`, which includes transcription (e.g., via Whisper for "Narración" or other methods for "Instrumental"/"Mixto" cases).
3.  The final transcript text has been stored in the `transcript_final` field of the `transcripts` table in the database.

The main entry point for this module is the `run_classification(conn, audio_path, operation)` function, which is called from `src/listener.py` after the `detect_music` stage.

## Step 1: Initialization and Configuration (`src/classify_categories.py`)

1.  **Load Configuration**:
    *   The script loads settings from `config/settings.json`, specifically the `gpt` section, which contains:
        *   `GPT_TEMPERATURE_CATEGORIES`: Temperature setting for the GPT call related to category/keyword generation.
        *   `GPT_PROMPT_CATEGORIES`: The template for the prompt that will be sent to GPT.
2.  **Azure OpenAI Client Setup**:
    *   It loads Azure OpenAI credentials (endpoint, deployment name, API key, API version) from environment variables (defined in `.env`).
    *   An `AzureOpenAI` client is initialized using these credentials.

## Step 2: Data Retrieval (`src/classify_categories.py` -> `run_classification`)

The `run_classification` function orchestrates the process:

1.  **Get Filename**: Extracts the `filename` from the input `audio_path` (e.g., `RRMM-69.wav`).
2.  **Fetch Transcript and Video Title**: Calls `get_final_transcript(filename, conn)` from `src/utils_db.py`.
    *   This utility function queries the database:
        *   It first looks up the `video_id` and `video_title` from the `videos` table using the filename (adjusting `.wav` to `.mp4` for the lookup).
        *   Then, using the `video_id`, it retrieves `transcript_final` from the `transcripts` table.
    *   If any of these are not found, the function returns `None` for those values, and `run_classification` may abort.
3.  **Fetch Categories**: Calls `get_categories(conn)` from `src/utils_db.py`.
    *   This queries the `category` table to get a list of all available category names (e.g., "ALIMENTACIÓN SALUDABLE", "BIENESTAR MENTAL", etc.). This list will be part of the prompt for GPT.

## Step 3: GPT for Keywords and Categories (`src/classify_categories.py` -> `obtain_keywords_categories`)

If the necessary data (transcript, title, video ID) is available, this function is called:

1.  **Prompt Construction**:
    *   The `GPT_PROMPT_CATEGORIES` template (from `config/settings.json`) is used.
    *   Placeholders in the prompt are filled:
        *   `{{CATEGORIES}}`: Replaced with a comma-separated string of category names fetched in Step 2.3.
        *   `{video_title}`: Replaced with the video's title.
        *   `{transcript}`: Replaced with the `final_transcript`.
    *   The prompt guides GPT to:
        *   Extract a list of relevant keywords.
        *   Select one (or a few if strictly necessary) categories from the provided list.
        *   Return the output in a specific JSON format: `{"keywords": ["kw1", ...], "categories": ["cat1", ...]}`.
2.  **API Call to Azure OpenAI**:
    *   An API call is made to `client.chat.completions.create()`.
    *   `model`: The Azure deployment name.
    *   `messages`: A list containing a single message with `role: "system"` and `content: prompt`.
    *   `temperature`: Set to `GPT_TEMPERATURE_CATEGORIES`.
3.  **Response Parsing**:
    *   The content from GPT's response (`response.choices[0].message.content`) is extracted.
    *   The `extract_json_block(content)` helper function is used to clean up potential Markdown formatting (like ` ```json ... ``` `) around the JSON output.
    *   The cleaned string is parsed using `json.loads()`.
4.  **Return Value**: Returns a dictionary containing:
    *   `keywords`: List of keywords from GPT.
    *   `categories`: List of categories from GPT.
    *   `prompt`: The full prompt sent to GPT.
    *   `temperature`: The temperature used.
    *   `tokens_input`, `tokens_output`: Token usage information from the API response.
    *   Returns `None` if the OpenAI call fails.

## Step 4: Storing Keywords and Categories (`src/classify_categories.py` -> `run_classification`)

If `obtain_keywords_categories` returns a valid `gpt_response`:

1.  **Call `store_keywords_categories`**: This function from `src/utils_db.py` is called with the `conn`, `video_id`, and the keywords, categories, and GPT metadata from `gpt_response`, along with the `operation` type (`create` or `modify`).

## Step 5: Database Update - Keywords & Categories (`src/utils_db.py` -> `store_keywords_categories`)

This database utility function performs the following:

1.  **Handle `modify` Operation**: If `operation` is "modify", it first deletes any existing keywords from `video_keywords` and categories from `video_categories` for the given `video_id`. This ensures that modifications replace old data rather than appending.
2.  **Insert Keywords**: Iterates through the list of `keywords` and inserts each one into the `video_keywords` table, associated with the `video_id`.
3.  **Insert Categories**: Iterates through the list of `categories`:
    *   For each category name, it first queries the `category` table to find its `category_id`.
    *   If found, it inserts a record into the `video_categories` table, linking `video_id` and `category_id`.
4.  **Update GPT Metadata**: Updates the `transcripts` table for the given `video_id` with:
    *   `gpt_prompt`: The prompt used.
    *   `gpt_temperature`: The temperature setting.
    *   `tokens_input`, `tokens_output`: Token usage.

## Step 6: GPT for Suggested Title and Description (`src/classify_categories.py` -> `suggest_title_description`)

After processing keywords and categories, `run_classification` then calls `suggest_title_description(video_title, final_transcript)`:

1.  **Prompt Construction**:
    *   A specific prompt is formatted (hardcoded within this function) that takes the original `video_title` and `final_transcript`.
    *   It asks GPT to suggest:
        1.  A new, more attractive title for social media.
        2.  A brief description (max 250 characters).
    *   It requests the response in JSON format with keys `"title"` and `"description"`.
2.  **API Call to Azure OpenAI**: Similar to keyword/category generation, but with a fixed temperature of `0.6`.
3.  **Response Parsing**: The JSON response is extracted and parsed.
4.  **Return Value**: Returns a dictionary like `{"title": "suggested title", "description": "suggested description"}` or `None` if the call fails.

## Step 7: Storing Suggested Title and Description (`src/classify_categories.py` -> `run_classification`)

If `suggest_title_description` returns a valid `title_description` dictionary:

1.  **Call `store_suggested_title_description`**: This function from `src/utils_db.py` is called with `conn`, `video_id`, and the suggested title and description.

## Step 8: Database Update - Suggested Title/Description (`src/utils_db.py` -> `store_suggested_title_description`)

This utility function updates the `videos` table for the given `video_id`, setting the `suggested_title` and `suggested_description` fields.

## Overall Flow Summary for Classification

1.  The `final_transcript` and `video_title` are fetched from the database.
2.  A list of all possible categories is also fetched.
3.  These are combined into a detailed prompt for Azure OpenAI (GPT) to extract keywords and select relevant categories.
4.  The GPT response (keywords and categories) is parsed and stored in `video_keywords` and `video_categories` tables. Metadata about the GPT call (prompt, temperature, tokens) is saved in the `transcripts` table.
5.  A separate call to GPT is made to generate a new, more engaging title and a short description for the video.
6.  These suggested texts are then stored in the `videos` table.

This completes the classification part of the pipeline, enriching the video's record with structured keywords, assigned categories, and AI-generated suggestions for title and description.

## Key Files, Functions, and Configurations for Classification

This section summarizes the most relevant components for the category and keyword classification process:

**1. Core Python Modules (`src/` directory):**

*   **`classify_categories.py`**: (Main orchestrator for this stage)
    *   `run_classification(conn, audio_path, operation)`: The primary function that:
        *   Calls `get_final_transcript()` and `get_categories()` (from `src/utils_db.py`) to fetch necessary data.
        *   Calls `obtain_keywords_categories()` to get keywords and categories from GPT.
        *   Calls `store_keywords_categories()` (from `src/utils_db.py`) to save them.
        *   Calls `suggest_title_description()` to get a new title/description from GPT.
        *   Calls `store_suggested_title_description()` (from `src/utils_db.py`) to save them.
    *   `obtain_keywords_categories(final_transcript, video_title, categories)`:
        *   Constructs the detailed prompt using `GPT_PROMPT_CATEGORIES` from settings.
        *   Makes the API call to Azure OpenAI (`client.chat.completions.create()`).
        *   Parses the JSON response (using `extract_json_block()`).
    *   `suggest_title_description(video_title, final_transcript)`:
        *   Constructs a specific prompt for title/description generation.
        *   Makes the API call to Azure OpenAI.
        *   Parses the JSON response.
    *   `extract_json_block(text)`: Helper to clean JSON responses from Markdown formatting.
*   **`utils_db.py`** (Database interactions related to classification):
    *   `get_final_transcript(filename, conn)`: Retrieves `transcript_final` (from `transcripts` table) and `video_title`, `video_id` (from `videos` table).
    *   `get_categories(conn)`: Fetches all category names from the `category` table.
    *   `store_keywords_categories(conn, video_id, keywords, categories, prompt, temperature, tokens_input, tokens_output, operation)`: Inserts keywords into `video_keywords`, category links into `video_categories` (after looking up `category_id`), and updates GPT metadata in the `transcripts` table.
    *   `store_suggested_title_description(conn, video_id, title, description)`: Updates `suggested_title` and `suggested_description` in the `videos` table.
*   **`config_loader.py`** (Used by `listener.py` and indirectly by other modules if they were to load settings independently, though `classify_categories.py` loads settings directly):
    *   `load_settings()`: Loads the `config/settings.json` file.

**2. Configuration Files:**

*   **`.env`** (in the project root):
    *   `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`: Credentials and endpoint details for the Azure OpenAI service.
*   **`config/settings.json`**:
    *   `"gpt"` section:
        *   `"temperature_categories"`: Temperature for the keywords/categories GPT prompt.
        *   `"prompt_categories"`: The detailed template for the keywords/categories prompt. This is a crucial piece of configuration defining how GPT is instructed.
        *   (Other GPT prompts like `"prompt_frames"` exist but are not directly used in `classify_categories.py` for the main transcript classification, they are for OCR text cleaning in `detect_music.py`'s instrumental/mixto path).

**3. Key Directory Structure (relative to project root):**

*   `src/`: Contains all the core Python logic.
*   `config/`: Contains `settings.json`.

**4. External Libraries (Key Dependencies from `requirements.txt`):**

*   **`openai`**: The Python client library for interacting with OpenAI APIs (used here for Azure OpenAI).
*   **`python-dotenv`**: For loading environment variables from the `.env` file.
*   **`psycopg2-binary`**: For PostgreSQL database connection.

This overview should help in navigating the codebase related to the classification of video content using GPT.
