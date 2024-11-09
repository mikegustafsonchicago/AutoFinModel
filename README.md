# Project README

This project is an API-based system for processing and summarizing PDF data, dynamically managing tokens, and sending structured data to OpenAI’s API. The system carefully handles token constraints, dynamically selecting content based on token limits.

## Table of Contents
1. [Overview](#overview)
2. [Setup](#setup)
3. [Modules](#modules)
   - [app.py](#app-py)
   - [api_processing.py](#api-processing-py)
   - [prompt_builder.py](#prompt-builder-py)
   - [running_summary_manager.py](#running-summary-manager-py)
   - [config.py](#config-py)
   - [file_manager.py](#file-manager-py)
   - [json_manager.py](#json-manager-py)
   - [pdf_processing.py](#pdf-processing-py)
4. [Usage](#usage)

## Overview
The project allows users to upload PDF files, which are processed and summarized into structured data via OpenAI’s API. Token limits are carefully managed, dynamically selecting content within constraints.

## Setup
1. Clone the repository and navigate to the project directory.
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Set up environment variables in `config.py`, including `OPENAI_MODEL` and `UPLOAD_FOLDER`.
4. Start the application:
    ```bash
    python app.py
    ```
    This will run the Flask server on `localhost:5000`.

## Modules

### app.py
- **Purpose**: The main Flask application that defines API endpoints. It handles routes for:
  - `/api/upload_pdf`: Uploading PDFs.
  - `/api/openai`: Triggering API calls to OpenAI.
  - `/download_excel`: Downloading the generated Excel model.
- **Usage**: Run `app.py` to start the server and access it at `localhost:5000`.

### api_processing.py
- **Purpose**: Manages the workflow for OpenAI API calls. This includes dynamically selecting PDF pages based on token constraints and chunking content into requests.
- **Key Functions**:
  - `manage_api_calls`: Manages OpenAI calls, calculates available tokens, and chunks pages.
  - `prepare_payload`: Assembles the API request payload using the PromptBuilder.
  - `make_openai_api_call`: Sends requests to OpenAI’s API and handles responses.
- **Dependencies**: Relies on `pdf_processing.py` for token counts and page content extraction, and `PromptBuilder` for structured prompt creation.

### prompt_builder.py
- **Purpose**: Constructs and manages prompt components, building the system and user prompts with context and PDF data.
- **Key Functions**:
  - `add_table_data`: Adds structured data (e.g., tables) to the prompt.
  - `get_system_prompt` and `get_user_prompt`: Generate complete prompts for OpenAI.
  - `get_token_count`: Calculates the token count for individual prompt components.
- **Dependencies**: Uses `file_manager.py` for file I/O and `json_manager.py` to load JSON explanations for tables.

### running_summary_manager.py
- **Purpose**: Manages the running summary that accumulates across API calls.
- **Key Functions**:
  - `get_summary`: Retrieves or initializes the running summary from a file.
  - `update_summary`: Appends new content to the running summary.
- **Dependencies**: Uses `file_manager.py` for file I/O.

### config.py
- **Purpose**: Contains project configuration settings, such as file paths, directories, token limits, and constants.
- **Key Variables**:
  - `MAX_TOKENS_PER_CALL`: Sets the maximum token limit for API calls.
  - `TABLE_MAPPING`: Maps table identifiers to JSON files.
  - `RUNNING_SUMMARY_FILE`: File path for storing the running summary.
- **Usage**: Adjust values here as needed for your setup, such as `UPLOAD_FOLDER` or `MAX_TOKENS_PER_CALL`.

### file_manager.py
- **Purpose**: Provides helper functions for reading and writing files, ensuring directories exist as required.
- **Key Functions**:
  - `write_file` and `read_file`: Handle basic file I/O.
  - `load_table_data`: Loads data from JSON files based on `TABLE_MAPPING`.
  - `initialize_session_files`: Initializes files for a new user session.
- **Dependencies**: Works with `json_manager.py` for JSON-specific functions.

### json_manager.py
- **Purpose**: Handles loading, updating, and saving structured JSON data (e.g., CAPEX, OPEX, employees).
- **Key Functions**:
  - `initialize_json_files`: Initializes JSON files with placeholder data.
  - `load_table_json`: Loads a specific JSON file based on `TABLE_MAPPING`.
  - `update_json_files`: Updates JSON files with new data.
  - `fix_incomplete_json`: Validates and corrects JSON formatting.
- **Usage**: Called primarily by `api_processing.py` to manage structured data updates.

### pdf_processing.py
- **Purpose**: Extracts text from PDFs and provides token counts for individual pages.
- **Key Functions**:
  - `extract_pdf_pages`: Retrieves text for each page in a PDF.
  - `get_page_token_counts`: Calculates token counts for each page for dynamic page selection.
  - `get_pdf_content_by_page_indices`: Extracts specified pages based on start and end indices.
- **Dependencies**: Uses `tiktoken` for token counting, integrated with OpenAI’s model.

## Usage
- **Upload PDF**: `POST` a PDF to `/api/upload_pdf`. This saves the file and returns a confirmation.
- **Trigger API Calls**: `POST` to `/api/openai` with desired parameters. `api_processing.py` will dynamically select PDF pages and manage token constraints, then send the structured prompt to OpenAI.
- **Download Excel Model**: `GET` `/download_excel` to download the generated financial model.

This project uses careful token management to stay within OpenAI’s token limits while providing summaries and structured data. Each module plays a specific role, creating a modular and maintainable codebase.
