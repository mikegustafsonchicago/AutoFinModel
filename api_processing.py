# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 14:19:25 2024

@author: mikeg
"""
import os
import json
import requests
import logging
from config import MAX_TOKENS_PER_CALL, RUNNING_SUMMARY_FILE, OPENAI_MODEL, DEFAULT_project_type, CATALYST_TABLE, FINANCIALS_TABLE, REAL_ESTATE_TABLE
from pdf_processing import get_page_token_counts, get_pdf_content_by_page_indices
from prompt_builder import PromptBuilder
from os import getenv
from dotenv import load_dotenv
from context_manager import get_user_context
from file_manager import get_project_data_path, get_project_structures_path
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("pdfplumber").setLevel(logging.WARNING)

def manage_api_calls(business_description, user_input, update_scope="all", file_name=None, prompt_manager=None, json_manager=None):
    
    """
    Manages API calls to OpenAI, dynamically selecting pages based on token count.
    """
    context = get_user_context()
    project_type = context.project_type
    project_name = context.current_project
    username = context.username
    
    # Ensure prompt_manager is passed and used within this function
    if prompt_manager is None:
       raise ValueError("prompt_manager must be initialized and passed to manage_api_calls.")
    
    # Load the base prompt first
    prompt_manager.load_prompt_file()
    prompt_manager.reset_prompts()   
    #Initialize the output variable
    openAI_output = {"text": "", "json_data": {}}
    

    # Get list of available tables from project data directory
    data_path = get_project_data_path()
    if not data_path:
        logging.error("Could not get project data path")
        return {"error": "Project data path not found"}, 404
        
    # Get list of table files and strip .json suffix
    all_tables = []
    if os.path.exists(data_path):
        all_tables = [f.replace('.json', '') for f in os.listdir(data_path)
                     if os.path.isfile(os.path.join(data_path, f)) and f.endswith('.json')]
    
    if not all_tables:
        logging.error("No table data files found")
        return {"error": "No table data available"}, 404

    # Determine which tables to update vs use as context
    update_tables = all_tables if update_scope == "all" else [update_scope]
    logging.debug(f"Update tables are {update_tables}")
    context_tables = [table for table in all_tables if table not in update_tables]

    # Load data for tables being updated and context tables
    tables_data = {
        table: json_manager.load_json_data(table) for table in update_tables
    }
    context_data = {
        table: json_manager.load_json_data(table) for table in context_tables
    }
    
    #Get the running summary to feed into the prompt
    running_summary = prompt_manager.get_summary()
    # Initialize the prompt manager and add basic components
    prompt_manager.update_system_prompt_info(
                                            update_tables=tables_data, 
                                            context_tables=context_data, 
                                            summary=running_summary, 
                                            business_description=business_description
                                            )
    prompt_manager.update_user_input(user_input)
    
    # Calculate overhead token count
    syetem_prompt_tokens = prompt_manager.get_token_count('system')
    user_inupt_tokens = prompt_manager.get_token_count('user')
    logging.info(f"Estimated system prompt [before payload] token count: {syetem_prompt_tokens} tokens")
    logging.info(f"Estimated user prompt token count: {user_inupt_tokens} tokens")
    logging.debug(f"User prompt is {prompt_manager.user_input}")
    
    # Total tokens available for PDF pages
    available_tokens_for_pdf = MAX_TOKENS_PER_CALL - (syetem_prompt_tokens + user_inupt_tokens)
    if available_tokens_for_pdf <= 0:
        logging.error("Not enough token space available for any PDF content.")
        return {"error": "Token limit exceeded without PDF content"}, 400


    # Get token counts for each page if PDF is provided
    page_token_counts = get_page_token_counts(file_name) if file_name else []
    page_index = 0  # Start from the first page

    #Use the list of pdf page token counts to bundle the pages into chunks
    chunk_list=[]
    start_page=0 #first start page for first chunk is page 0
    active_chunk_dict = {"start_page":start_page, "end_page":start_page, "token_count":0}
    tokens_remaining = available_tokens_for_pdf
    for page_num, token_count in enumerate(page_token_counts):
        logging.info(f"For page {page_num}, the token count is: {token_count}")
        
        if token_count < tokens_remaining: 
            #Update the active_chunk_dict
            active_chunk_dict['end_page'] = page_num
            active_chunk_dict['token_count'] += token_count
        else:
            chunk_list.append(active_chunk_dict)
            active_chunk_dict = {"start_page":page_num, "end_page":page_num, "token_count":token_count}
        
        if page_num == len(page_token_counts)-1:
            #If it's the final page
            chunk_list.append(active_chunk_dict)
    
    
    for chunk_dict in chunk_list:
        # Get PDF content for this chunk using updated function signature
        chunk_text = get_pdf_content_by_page_indices(
            file_name=file_name,
            start_page=chunk_dict['start_page'],
            end_page=chunk_dict['end_page']
        ) if file_name else None
        
        prompt_manager.add_pdf_chunk(chunk_text)

        # Make the API call and process the response
        response, status_code = manage_call_for_payload(chunk_text, chunk_dict['start_page'], chunk_dict['end_page'], json_manager, prompt_manager=prompt_manager)
        if status_code != 200:
            return response, status_code

    #This is for debugging
    prompt_manager.write_system_prompt()

    # Update the final summary and JSON data
    openAI_output["text"] += response.get("text", "")
    openAI_output["json_data"].update(response.get("JSONData", {}))
    prompt_manager.display_tokens_and_cost(openAI_output)

    # Update JSON files with the aggregated data
    json_manager.update_json_files(openAI_output["json_data"])
    return openAI_output, 200





def manage_call_for_payload(pdf_chunk, page_start, page_end, json_manager, prompt_manager, project_type=None):
    """
    Processes each chunk of data with OpenAI API
    """
    # Ensure prompt_manager is passed and used within this function
    if prompt_manager is None:
       raise ValueError("Error from prepare_payload: prompt_manager must be initialized and passed to manage_api_calls.")
    system_prompt = prompt_manager.get_system_prompt()
    user_prompt = prompt_manager.get_user_prompt()

    raw_response, status_code = make_openai_api_call(system_prompt=system_prompt, user_prompt=user_prompt)
    logging.debug(f"manage_call_for_payload: raw_response: {raw_response}")
    
    if status_code != 200:
        logging.error(f"API call failed: {raw_response}")
        return {"error": "API call failed"}, status_code

    processed_response, _ =  handle_openai_response(raw_response, json_manager, prompt_manager)
    json_data = processed_response.get("JSONData", {})
    #Update the JSON Files
    json_manager.update_json_files(json_data)
    
    logging.info(f"---------- END PAGES {page_start} THROUGH {page_end} -----------\n\n")
    return processed_response, status_code



def make_openai_api_call(system_prompt, user_prompt):
    """
    Makes the actual API call to OpenAI and returns the response.
    """
    load_dotenv()
    api_key = getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 5000
    }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    if not system_prompt:
        return {"error": "System prompt not found. Did not call openAI"}, 500
    
    
    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
        if response.status_code == 200:
            return response.json(), 200
        else:
            return {"error": "OpenAI API call failed", "details": response.text}, response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred during API request: {e}")
        return {"error": "Request failed", "details": str(e)}, 500


# Function to handle the OpenAI API response
def handle_openai_response(response, json_manager, prompt_manager):
    response_json = response

    # Extract the AI response content
    ai_content = response_json['choices'][0]['message']['content']
    try:
        
        #Debug feature. Write response to txt
        save_directory = os.path.join(os.getcwd())
        txt_file_path = os.path.join(save_directory, 'DEBUG_FILE_openai_response.txt')
        with open(txt_file_path, 'w', encoding='utf-8') as f:
            f.write(ai_content)

        
        # Split the content to extract the JSON part
        text_part = ai_content.split('### TEXT END ###')[0].replace('### TEXT START ###', '').strip()
        json_part = ai_content.split('---JSON END---')[0].split('---JSON START---')[1].strip()
        running_summary = ai_content.split('### SUMMARY END ###')[0].split('### SUMMARY START ###')[1].strip()
        prompt_manager.update_summary(running_summary)
        
        # Fix incomplete JSON by adding missing brackets if necessary
        json_part = json_manager.fix_incomplete_json(json_part)

        # Parse the JSON content
        parsed_data = json.loads(json_part)
        
        # Validate that parsed_data is a dictionary
        if isinstance(parsed_data, list):
           logging.error("OpenAI response returned a list; expected a dictionary for table data.")
           raise ValueError("Invalid response format: Expected a dictionary, received a list.")
       
        
        # Save the JSON data to the file system
        json_manager.save_json_to_file(parsed_data)
        
        # Save the running summary

        # Return both text and expenses back to the caller
        return {"text": text_part, "JSONData": parsed_data}, 200
    except (json.JSONDecodeError, IndexError):
        return {"error": "Failed to parse JSON from AI response"}, 400

def extract_text_from_response(response):
    """
    Extracts the relevant text (message content) from the OpenAI API response.
    """
    try:
        # The actual content from the response is usually in this field
        return response['choices'][0]['message']['content']
    except (KeyError, IndexError) as e:
        logging.error(f"Error extracting text from response: {e}")
        return ""
