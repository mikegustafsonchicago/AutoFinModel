# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 14:19:25 2024
@author: mikeg

This module manages calls to the OpenAI API, handles PDF content chunking, updates JSON data,
and integrates prompt management and summarization steps.
"""

import os
import json
import requests
import logging
from logging.handlers import RotatingFileHandler  # Import RotatingFileHandler
from os import getenv
from dotenv import load_dotenv
from flask import session
from datetime import datetime

# Local imports
from config import (
    OPENAI_API_KEY,
    MAX_TOKENS_PER_CALL, 
    OPENAI_MODEL, 
    DEFAULT_project_type, 
)
from pdf_processing import get_page_token_counts, get_pdf_content_by_page_indices
from prompt_builder import PromptBuilder
from file_manager import get_project_data_path, list_s3_directory_contents, write_file, list_project_data_files
from upload_file_manager import count_tokens

#=============================================================
# LOGGING CONFIGURATION
#=============================================================

# Create a logger for this module
logging.getLogger(__name__).setLevel(logging.DEBUG)  # Set minimum logging level to DEBUG for more verbose output

# Suppress lower-level logs from specific libraries to reduce noise
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("pdfplumber").setLevel(logging.WARNING)

#The rest of the initialization is done in the initialize_module_logging function, to prevent circular imports

#=============================================================
# FUNCTION DEFINITIONS
#=============================================================

def manage_api_calls(business_description, user_input, update_scope="all", file_name=None, prompt_manager=None, json_manager=None):
    NUMBER_OF_UPDATE_TABLES_PER_CALL = 2
    SEND_CONTEXT_TABLES_TO_OPENAI = False
    """
    Main function to manage API calls to OpenAI. Handles:
    - Loading context and determining tables to update
    - Preparing prompts with JSON data and user input 
    - Chunking PDF content and making API calls
    - Processing responses and updating data

    Parameters
    ----------
    business_description : str
        Description of the business/project context
    user_input : str 
        User's query or prompt
    update_scope : str, optional
        Which tables to update (default "all")
    file_name : str, optional
        Path to PDF file, if any
    prompt_manager : PromptBuilder
        Required - manages prompts and tokens
    json_manager : JsonManager
        Required - handles JSON data

    Returns
    -------
    tuple (dict, int)
        Output dictionary and HTTP status code
    """

    logging.debug("Starting manage_api_calls function with params:")
    logging.debug(f"business_description: {business_description[:100] if business_description else 'None'}...")
    logging.debug(f"user_input: {user_input}")
    logging.debug(f"update_scope: {update_scope}")
    logging.debug(f"file_name: {file_name}")

    # Get and validate project type immediately
    current_project = session.get('current_project', {})
    project_type = current_project.get('type')
    
    logging.debug("Session state at start of manage_api_calls:")
    logging.debug(f"Current project data: {current_project}")
    logging.debug(f"Project type value: {project_type}")
    
    # Store project type locally to prevent it from changing
    if not project_type:
        logging.error(f"No project type found in session current_project: {current_project}")
        return {"error": "Project type not set"}, 400

    # Validate project type with explicit comparison
    valid_types = ['financial', 'catalyst', 'real_estate', 'ta_grading']
    if project_type not in valid_types:
        logging.error(f"Invalid project type: '{project_type}'. Must be one of: {valid_types}")
        return {"error": f"Invalid project type: {project_type}"}, 400

    # Continue with validated project_type
    external_utities_check = initialize_and_check_external_utilities(prompt_manager, json_manager, project_type)
    logging.debug(f"External utilities check result: {external_utities_check}")
    
    if not external_utities_check:
        logging.error("Failed to initialize external utilities.")
        return {"error": "Failed to initialize utilities"}, 500
    
    # Add user's input to the user prompt
    prompt_manager.update_user_input(user_input)
    prompt_manager.update_system_prompt_info(business_description=business_description)
    logging.debug("Updated prompt manager with user input and system prompt info")

    # Initialize the output container
    data_path = get_project_data_path()  # Error handling in initialize_and_check_external_utilities
    logging.debug(f"Retrieved data path: {data_path}")

    # Create the update and context tables data as a dictionary
    update_tables_data, context_tables_data = get_tables_data(data_path, json_manager, update_scope)
    logging.debug(f"Retrieved tables data - Update tables: {list(update_tables_data.keys())}")
    logging.debug(f"Context tables: {list(context_tables_data.keys())}")

    logging.info(f"The update tables are: {list(update_tables_data.keys())}")
    logging.info(f"Here's the list of context tables: {list(context_tables_data.keys())}")

    # Break the tables into groups of NUMBER_OF_UPDATE_TABLES_PER_CALL and find out the max token count for the group + the base prompt  + (optional) the context tables
    max_table_group_token_count = get_table_group_token_list(update_tables_data, context_tables_data, business_description, NUMBER_OF_UPDATE_TABLES_PER_CALL, SEND_CONTEXT_TABLES_TO_OPENAI, prompt_manager)
    logging.debug(f"Max table group token count: {max_table_group_token_count}")
    
    # Determine how many tokens remain for PDF content
    available_tokens_for_pdf = MAX_TOKENS_PER_CALL - max_table_group_token_count
    logging.debug(f"Available tokens for PDF content: {available_tokens_for_pdf}")
    
    if available_tokens_for_pdf <= 0:
        logging.error("Not enough token space available for PDF content.")
        return {"error": "Token limit exceeded without PDF content"}, 400

    chunk_list = process_pdf_into_chunks(file_name, available_tokens_for_pdf)
    logging.debug(f"Generated chunk list with {len(chunk_list)} chunks")
    logging.info(f"Chunk list: {chunk_list}")

    # Example of logging dynamic data
    page_groups = [{"start_page": chunk["start_page"], "end_page": chunk["end_page"], "token_count": chunk["token_count"]} for chunk in chunk_list]
    logging.info(f"Here's the list of page groups and their associated counts: {page_groups}")

    result, status_code = send_tables_and_chunks_to_openai(
        chunk_list,
        update_tables_data,
        context_tables_data,
        business_description,
        prompt_manager,
        json_manager,
        file_name,
        NUMBER_OF_UPDATE_TABLES_PER_CALL,
        SEND_CONTEXT_TABLES_TO_OPENAI
    )
    
    # Add safety check before logging
    logging.debug(f"Final result status: {status_code}")
        
    return result, status_code  # Make sure to return both values




def initialize_and_check_external_utilities(prompt_manager, json_manager, project_type):
    # Validate prompt_manager and json_manager
    initialize_module_logging()

    if prompt_manager is None:
        raise ValueError("prompt_manager must be initialized and passed to manage_api_calls.")
        return False
    if json_manager is None:
        raise ValueError("json_manager must be initialized and passed to manage_api_calls.")
        return False
        
    if not project_type:
        raise ValueError("project_type must be set before initializing utilities.")
        return False

    #Setup prompt manager with project type
    prompt_manager.project_type = project_type
    prompt_manager.load_static_prompt_file()
    prompt_manager.reset_prompts()

    #Check the data path
    data_path = get_project_data_path()
    if not data_path:
        logging.error("Could not get project data path.")
        return False
    return True
    prompt_manager.load_static_prompt_file()
    prompt_manager.reset_prompts()

    #Check the data path
    data_path = get_project_data_path()
    if not data_path:
        logging.error("Could not get project data path.")
        return False
    return True

def initialize_module_logging():
    # Create a StreamHandler (logs to console)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logging.getLogger(__name__).addHandler(stream_handler)

def get_tables_data(data_path, json_manager, update_scope="all"):
    logging.debug(f"Getting tables data from {data_path} with update_scope: {update_scope}")
    
    # Use new function to get only data files
    s3_files = list_project_data_files(data_path)
    logging.debug(f"Retrieved data files: {s3_files}")
    
    if not s3_files:
        logging.error("No table data files found.")
        return {"error": "No table data available"}
        
    all_tables = [os.path.splitext(os.path.basename(f))[0] for f in s3_files]
    
    # Determine which tables to update vs. use as context
    update_tables = all_tables if update_scope == "all" else [update_scope]
    context_tables = [table for table in all_tables if table not in update_tables]
    
    logging.debug(f"Update tables: {update_tables}")
    logging.debug(f"Context tables: {context_tables}")

    # Load JSON data for update and context tables
    tables_data = {table: json_manager.load_json_data(table) for table in update_tables}
    context_data = {table: json_manager.load_json_data(table) for table in context_tables}
    
    logging.debug(f"Loaded {len(tables_data)} update tables and {len(context_data)} context tables")
    return tables_data, context_data

def get_table_group_token_list(update_tables_data, context_tables_data, business_description, NUMBER_OF_UPDATE_TABLES_PER_CALL, SEND_CONTEXT_TABLES_TO_OPENAI, prompt_builder):
    """
    Creates groups of table indices and their token counts based on update table limits.

    Parameters
    ----------
    update_tables_data : dict
        Dictionary of tables that need to be updated
    context_tables_data : dict 
        Dictionary of tables providing context
    NUMBER_OF_UPDATE_TABLES_PER_CALL : int
        Maximum number of tables to update per API call
    SEND_CONTEXT_TABLES_TO_OPENAI : bool
        Whether to include context tables in token count
    prompt_builder : PromptBuilder
        Instance of PromptBuilder to get static prompt tokens

    Returns
    -------
    list
        List of tuples containing (start_idx, end_idx, token_count) for each group
    """
    logging.debug("Starting get_table_group_token_list calculation")
    
    table_groups = []
    update_tables = list(update_tables_data.keys())
    logging.debug(f"Processing {len(update_tables)} update tables")
    
    # Calculate total token count from context tables
    context_token_count = 0
    for table_name, table_data in context_tables_data.items():
        table_tokens = count_tokens(json.dumps(table_data))
        context_token_count += table_tokens
        logging.debug(f"Context table {table_name} token count: {table_tokens}")

    # Get static prompt token count
    static_prompt_tokens = count_tokens(prompt_builder.system_prompt) if prompt_builder.system_prompt else 0
    user_prompt_tokens = count_tokens(prompt_builder.user_prompt) if prompt_builder.user_prompt else 0 
    business_description_tokens = count_tokens(business_description) if business_description else 0
    
    logging.debug(f"Static prompt tokens: {static_prompt_tokens}")
    logging.debug(f"User prompt tokens: {user_prompt_tokens}")
    logging.debug(f"Business description tokens: {business_description_tokens}")

    # Group update tables
    for i in range(0, len(update_tables), NUMBER_OF_UPDATE_TABLES_PER_CALL):
        end_idx = min(i + NUMBER_OF_UPDATE_TABLES_PER_CALL, len(update_tables))
        group_token_count = static_prompt_tokens + user_prompt_tokens + business_description_tokens 
        
        # Add token count for tables in this group
        for j in range(i, end_idx):
            table_name = update_tables[j]
            table_tokens = count_tokens(json.dumps(update_tables_data[table_name]))
            group_token_count += table_tokens
            logging.debug(f"Update table {table_name} token count: {table_tokens}")
        
        # Add context token count if enabled
        if SEND_CONTEXT_TABLES_TO_OPENAI:
            group_token_count += context_token_count
            logging.debug(f"Added context token count: {context_token_count}")
            
        table_groups.append((i, end_idx - 1, group_token_count))
        logging.debug(f"Created group {len(table_groups)}: {(i, end_idx - 1, group_token_count)}")
        
    logging.info(f"Table groups: {table_groups}")
    max_tokens = max(group[2] for group in table_groups) if table_groups else 0
    return max_tokens
    
def process_pdf_into_chunks(file_name, available_tokens_for_pdf):
    logging.info(f"Processing PDF: {file_name}")
    page_token_counts = get_page_token_counts(file_name) if file_name else []

    logging.info(f"Processing PDF into chunks. Total pages: {len(page_token_counts)}")
    # Chunk the PDF pages to fit into available token space
    chunk_list = []
    active_chunk = {"start_page": 0, "end_page": 0, "token_count": 0}
    
    chunk_summary = []
    for page_num, token_count in enumerate(page_token_counts):
        # If adding this page fits within the token budget for current chunk
        if active_chunk['token_count'] + token_count < available_tokens_for_pdf:
            active_chunk['end_page'] = page_num
            active_chunk['token_count'] += token_count
        else:
            # Start a new chunk since adding this page would exceed the limit
            chunk_list.append(active_chunk)
            chunk_summary.append(f"Chunk {len(chunk_list)}: Pages {active_chunk['start_page']}-{active_chunk['end_page']} ({active_chunk['token_count']} tokens)")
            active_chunk = {"start_page": page_num, "end_page": page_num, "token_count": token_count}

        # If it's the final page, push the last chunk
        if page_num == len(page_token_counts) - 1:
            chunk_list.append(active_chunk)
            chunk_summary.append(f"Chunk {len(chunk_list)}: Pages {active_chunk['start_page']}-{active_chunk['end_page']} ({active_chunk['token_count']} tokens)")
    
    logging.info("PDF chunk summary:\n" + "\n".join(chunk_summary))
            
    logging.info(f"Created {len(chunk_list)} chunks from PDF")
    return chunk_list

def send_tables_and_chunks_to_openai(
    chunk_list,
    update_tables_data,
    context_tables_data,
    business_description,
    prompt_manager,
    json_manager,
    file_name=None,
    number_tables_per_call=2,
    send_context_tables=False
):
    """
    Loops over subsets of update tables based on number_tables_per_call,
    and over the PDF chunks in chunk_list.
    
    For each subset of update tables:
      1) Prepare the prompt with those tables (and context if enabled).
      2) For each PDF chunk, add chunk text, call the API, and aggregate results.

    Parameters
    ----------
    chunk_list : list of dict
        Each dict has { "start_page": int, "end_page": int, "token_count": int }.
    update_tables_data : dict
        {table_name: table_json_data} for all tables that need updates.
    context_tables_data : dict
        {table_name: table_json_data} for context tables, if needed.
    business_description : str
        Overall business description to inject into the prompt if desired.
    prompt_manager : PromptBuilder
        Manages prompt text/tokens (unchanged logic).
    json_manager : JsonManager
        Loads/saves JSON data (unchanged logic).
    file_name : str or None
        Path to the PDF file, if needed for chunk text extraction.
    number_tables_per_call : int
        How many update tables to include in each call (or chunk of calls).
    send_context_tables : bool
        Whether to add context_tables_data to each prompt call.

    Returns
    -------
    dict
        A dictionary containing:
        - success: bool indicating if all operations completed successfully
        - message: str with details about the operation
        - data: dict containing the aggregated results if successful
        - errors: list of any errors encountered
    """
    result = {
        "success": True,
        "message": "",
        "data": {"text": "", "json_data": {}},
        "errors": []
    }

    logging.info(f"Starting OpenAI processing with {len(chunk_list)} chunks and {len(update_tables_data)} tables")
    logging.debug(f"Send context tables: {send_context_tables}")
    logging.debug(f"Number of tables per call: {number_tables_per_call}")

    # Convert update_tables_data keys into a list
    all_update_table_names = list(update_tables_data.keys())
    logging.debug(f"Update table names: {all_update_table_names}")
    
    # Process table subsets
    for i in range(0, len(all_update_table_names), number_tables_per_call):
        subset_names = all_update_table_names[i : i + number_tables_per_call]
        logging.info(f"Processing table subset {i//number_tables_per_call + 1}/{(len(all_update_table_names) + number_tables_per_call - 1)//number_tables_per_call}: {subset_names}")

        current_subset_data = {name: update_tables_data[name] for name in subset_names}

        # Reset and prepare prompt manager
        prompt_manager.reset_prompts()
        prompt_manager.load_static_prompt_file()
        prompt_manager.update_system_prompt_info(
            update_tables=current_subset_data,
            context_tables=context_tables_data if send_context_tables else None,
            business_description=business_description
        )
        logging.debug("Updated prompt manager with current subset data")

        # Process PDF chunks for this table subset
        for chunk_idx, chunk_dict in enumerate(chunk_list):
            start_page = chunk_dict.get("start_page", None)
            end_page = chunk_dict.get("end_page", None)
            logging.info(f"Processing chunk {chunk_idx + 1}/{len(chunk_list)} (pages {start_page}-{end_page}) for table subset {subset_names}")

            # Extract chunk text if needed
            chunk_text = ""
            if file_name and start_page is not None and end_page is not None:
                chunk_text = get_pdf_content_by_page_indices(file_name, start_page, end_page)

            if chunk_text:
                prompt_manager.add_pdf_chunk(chunk_text)

            # Make API call
            response, status_code = manage_call_for_payload(
                pdf_chunk=chunk_text,
                page_start=start_page,
                page_end=end_page,
                json_manager=json_manager,
                prompt_manager=prompt_manager
            )
            logging.debug(f"API call completed with status code: {status_code}")

            if status_code != 200:
                error_msg = f"API call failed for chunk {chunk_idx + 1} (pages {start_page}-{end_page})"
                result["errors"].append(error_msg)
                result["success"] = False
                result["message"] = "Failed due to API errors"
                logging.error(error_msg)
                return result

            # Aggregate results
            result["data"]["text"] += response.get("text", "")
            result["data"]["json_data"].update(response.get("JSONData", {}))
            logging.debug(f"Updated result data with new response. Current JSON keys: {list(result['data']['json_data'].keys())}")

    # Final processing
    logging.info(f"Completed all processing. Processed {len(chunk_list)} chunks across {len(all_update_table_names)} tables")
    
    try:
        prompt_manager.display_tokens_and_cost(result["data"])
        json_manager.update_json_files(result["data"]["json_data"])
        result["message"] = "Successfully processed all chunks and tables"
        logging.debug("Final processing completed successfully")
        return result, 200
    except Exception as e:
        result["success"] = False
        result["message"] = f"Failed during final processing: {str(e)}"
        result["errors"].append(str(e))
        logging.error(f"Error during final processing: {str(e)}")
        return result, 500



def manage_call_for_payload(pdf_chunk, page_start, page_end, json_manager, prompt_manager, project_type=None):
    """
    Handles a single API call payload which may consist of multiple pages (a chunk).

    Parameters
    ----------
    pdf_chunk : str or None
        The extracted PDF text chunk to include in the prompt.
    page_start : int
        The starting page number of this chunk.
    page_end : int
        The ending page number of this chunk.
    json_manager : instance
        Manages loading/saving JSON.
    prompt_manager : PromptBuilder instance
        Handles prompt construction and token counts.
    project_type : str, optional
        The project type, if needed.

    Returns
    -------
    tuple (dict, int)
        The processed response and the HTTP status code.
    """

    
    if prompt_manager is None:
        logging.error("prompt_manager not provided to manage_call_for_payload")
        raise ValueError("prompt_manager must be provided to manage_call_for_payload.")

    # Retrieve the full system and user prompts
    system_prompt = prompt_manager.get_system_prompt()
    user_prompt = prompt_manager.get_user_prompt()

    # Make the API call with the current prompts
    raw_response, status_code = make_openai_api_call(system_prompt=system_prompt, user_prompt=user_prompt)
    
    if status_code != 200:
        logging.error(f"API call failed with status {status_code}: {raw_response}")
        return {"error": "API call failed"}, status_code

    # Process and handle the OpenAI response
    processed_response, _ = handle_openai_response(raw_response, json_manager, prompt_manager)
    json_data = processed_response.get("JSONData", {})
    
    json_manager.update_json_files(json_data)

    logging.info(f"Completed processing pages {page_start} through {page_end}.")
    return processed_response, status_code


def make_openai_api_call(system_prompt, user_prompt):
    """
    Makes an API call to OpenAI's chat completion endpoint.

    Parameters
    ----------
    system_prompt : str
        The system-level prompt content.
    user_prompt : str
        The user's prompt content.

    Returns
    -------
    tuple (dict, int)
        The OpenAI response JSON and HTTP status code.
    """
    logging.debug("Starting OpenAI API call")
    
    if not OPENAI_API_KEY:
        logging.error("OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 5000
    }

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }

    # If system prompt is missing, return an error
    if not system_prompt:
        logging.error("System prompt not found. OpenAI call aborted.")
        return {"error": "System prompt not found."}, 500

    # Perform the API request
    try:
        logging.debug(f"[{datetime.now().strftime('%H:%M:%S')}] Sending request to OpenAI API")
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
        logging.debug(f"[{datetime.now().strftime('%H:%M:%S')}] Received response with status code: {response.status_code}")
        
        if response.status_code == 200:
            return response.json(), 200
        else:
            logging.error(f"OpenAI API call failed with status {response.status_code}: {response.text}")
            return {"error": "OpenAI API call failed", "details": response.text}, response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during API request: {e}")
        return {"error": "Request failed", "details": str(e)}, 500


def handle_openai_response(response, json_manager, prompt_manager):
    """
    Parses and processes the OpenAI API response. Extracts text, JSON data, and summary.
    Saves JSON data to file, updates running summary, and returns structured data.

    Parameters
    ----------
    response : dict
        The raw response from the OpenAI API.
    json_manager : instance
        Manages saving/loading JSON data.
    prompt_manager : PromptBuilder instance
        Manages the prompt and summary.

    Returns
    -------
    tuple (dict, int)
        A tuple of processed response dict and status code.
        Processed response dict keys: "text", "JSONData"
    """
    logging.debug("Starting to handle OpenAI response")
    
    # Extract AI content
    try:
        ai_content = response['choices'][0]['message']['content']
    except (KeyError, IndexError):
        logging.error("Failed to extract content from the OpenAI response.")
        return {"error": "No usable content in response"}, 400

    # Debug: Save raw AI response to a text file
    save_directory = get_project_data_path()
    if save_directory:
        s3_path = f"{save_directory}/ai_responses/DEBUG_FILE_openai_response.txt"
        write_file(s3_path, ai_content)
    else:
        logging.error("Could not get project data path to save AI response")

    try:
        # Extract TEXT, JSON, and SUMMARY parts from AI response
        text_part = ai_content.split('### TEXT END ###')[0].replace('### TEXT START ###', '').strip()
        json_part_raw = ai_content.split('---JSON END---')[0].split('---JSON START---')[1].strip()
        running_summary = ai_content.split('### SUMMARY END ###')[0].split('### SUMMARY START ###')[1].strip()

        # Update the running summary in prompt_manager
        prompt_manager.update_summary(running_summary)
        logging.debug("Updated running summary in prompt manager")

        # Attempt to fix and parse JSON part
        json_part = json_manager.fix_incomplete_json(json_part_raw)
        parsed_data = json.loads(json_part)

        # Validate parsed JSON data type
        if isinstance(parsed_data, list):
            logging.error("OpenAI response returned a list; expected a dictionary for table data.")
            raise ValueError("Invalid response format: Expected dict but got list.")

        # Save the parsed JSON data
        json_manager.save_json_to_file(parsed_data)

        return {"text": text_part, "JSONData": parsed_data}, 200
    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logging.error(f"Error parsing OpenAI response: {e}")
        return {"error": "Failed to parse JSON from AI response"}, 400


def extract_text_from_response(response):
    """
    Safely extracts text content from the OpenAI API response object.

    Parameters
    ----------
    response : dict
        The response object from OpenAI.

    Returns
    -------
    str
        The extracted text content, or empty string if not found.
    """
    logging.debug("Attempting to extract text from response")
    try:
        text_content = response['choices'][0]['message']['content']
        logging.debug(f"Successfully extracted text content of length: {len(text_content)}")
        return text_content
    except (KeyError, IndexError) as e:
        logging.error(f"Error extracting text: {e}")
        return ""
