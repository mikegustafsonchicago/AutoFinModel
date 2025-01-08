# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:11:48 2024

@author: mikeg

prompt_builder.py

This module defines the PromptBuilder class, which is responsible for:
- Loading and assembling system and user prompts from various sources (project type, tables, PDFs, etc.).
- Managing running summaries and table data updates.
- Counting tokens and calculating cost estimates for OpenAI API calls.
- Writing prompts and summaries to the project data directory.
"""

import os
import json
import logging

from json_manager import JsonManager
from file_manager import (
    write_file, 
    get_project_data_path, 
    copy_prompt_to_project,
    list_s3_directory_contents,
    read_file,
    read_json
)
from config import OPENAI_COST_PER_INPUT_TOKEN, OPENAI_COST_PER_OUTPUT_TOKEN, BASE_PROMPT_DIR
from pdf_processing import count_tokens
from flask import session


class PromptBuilder:
    """
    PromptBuilder handles the construction and management of system and user prompts
    for an OpenAI-powered application. It integrates project context, table data,
    business descriptions, PDF content chunks, and running summaries into coherent prompts.
    """

    def __init__(self, json_manager):
        """
        Initialize a PromptBuilder instance.

        Parameters
        ----------
        json_manager : JsonManager
            An instance of JsonManager for loading/saving JSON data.
        """
        self.json_manager = json_manager
        self.static_prompt_text = ''
        self.system_prompt = ''
        self.project_type = None
        self.table_data = ''
        self.summary = ''
        self.pdf_chunk = ''
        self.chunk_num_text = ''
        self.business_description = ''
        self.user_input = ''
        self.user_prompt = ''
        self.running_summary = ''
        #Do not load the static prompt file on init. Causes circular import.

    # -------------------------------------------------------------------------
    # Initialization and Prompt File Loading
    # -------------------------------------------------------------------------

    def load_static_prompt_file(self):
        """
        Load the base prompt file from the project's data directory based on project type.
        If the prompt file does not exist, attempts to copy it from a base directory.
        """
        username = session.get('user', {}).get('username')
        current_project = session.get('current_project', {})
        
        # Get project type from current_project
        if not self.project_type:  # Only set if not already set
            self.project_type = current_project.get('type')
        

        prompt_path = get_project_data_path()

        # Determine prompt filename from project type
        if self.project_type == "financial":
            prompt_filename = "prompt.txt"
        elif self.project_type == "catalyst":
            prompt_filename = "catalyst_prompt.txt"
        elif self.project_type == "real_estate":
            prompt_filename = "real_estate_prompt.txt"
        elif self.project_type == "ta_grading":
            prompt_filename = "ta_grading_prompt.txt"
        else:
            logging.error(f"Invalid project type: {self.project_type}")
            raise ValueError(f"Invalid project type: {self.project_type}")

        # Construct S3 path for prompt file
        s3_prompt_path = f"{prompt_path}/{prompt_filename}"
        
        # Check if prompt file exists in S3 by trying to read it
        prompt_content = read_file(s3_prompt_path)
        if not prompt_content:
            success = copy_prompt_to_project()
            if not success:
                logging.error(f"Failed to copy prompt file for project type: {self.project_type}, initializing base system prompt.")
                self.initialize_base_system_prompt()
                return
        else:
            self.static_prompt_text = prompt_content.strip()
            return

        # Read the prompt file content
        with open(prompt_content, 'r') as file:
            self.static_prompt_text = file.read().strip()

    def initialize_base_system_prompt(self):
        """
        Initialize the base system prompt by copying a corresponding prompt file
        from BASE_PROMPT_DIR into the project's data directory, if available.
        """
        username = session.get('username')
        current_project = session.get('current_project')
        project_type = session.get('project_type')

        # Determine source prompt file based on project type
        if project_type == "catalyst":
            source_file = os.path.join(BASE_PROMPT_DIR, "catalyst_prompt.txt")
            dest_filename = "catalyst_prompt.txt"
        elif project_type == "real_estate":
            source_file = os.path.join(BASE_PROMPT_DIR, "real_estate_prompt.txt")
            dest_filename = "real_estate_prompt.txt"
        elif project_type == "financial":
            source_file = os.path.join(BASE_PROMPT_DIR, "prompt.txt")
            dest_filename = "prompt.txt"
        elif project_type == "ta_grading":
            source_file = os.path.join(BASE_PROMPT_DIR, "ta_grading_prompt.txt")
            dest_filename = "ta_grading_prompt.txt"
        else:
            logging.error(f"Invalid project type: {project_type}")
            return False

        # Construct S3 destination path
        dest_path = f"users/{username}/projects/{current_project}/data/{dest_filename}"

        try:
            # Read from local static folder
            if os.path.exists(source_file):
                with open(source_file, 'r', encoding='utf-8') as src:
                    content = src.read()
                    # Write to S3
                    success = write_file(dest_path, content)
                    if success:
                        logging.info(f"Copied system prompt file to S3: {dest_path}")
                        return True
                    else:
                        logging.error("Failed to write prompt file to S3")
                        return False
            else:
                logging.warning(f"Source prompt file not found in static folder: {source_file}")
                return False
        except Exception as e:
            logging.error(f"Error copying system prompt file: {e}")
            return False

    # -------------------------------------------------------------------------
    # Prompt and Summary Management
    # -------------------------------------------------------------------------

    def reset_prompts(self):
        """
        Reset all prompt components to their default empty values.
        """
        self.table_data = ''
        self.summary = ''
        self.pdf_chunk = ''
        self.chunk_num_text = ''
        self.business_description = ''
        self.user_input = ''
        self.user_prompt = ''
        self.running_summary = "This is the first call for this project and there is no running summary."

    def reset_system_prompt(self):
        self.system_prompt = ''
        self.table_data = ''
        self.pdf_chunk = ''
        self.chunk_num_text = ''

    def get_summary(self):
        """
        Retrieve the running summary from the project's data directory in S3.

        Returns
        -------
        str
            The current running summary text. If none exists, initializes and returns a default summary.
        """
        try:
            data_path = get_project_data_path()
            if data_path is None:
                logging.error("Could not get project data path.")
                return "This is the first call for this project and there is no running summary."

            summary_file = f"{data_path}/running_summary.txt"
            
            # Check if file exists in S3 by listing files with prefix
            if list_s3_directory_contents(summary_file):
                # Read summary from S3
                self.running_summary = read_file(summary_file)
            else:
                initial_summary = "This is the first call for this project and there is no running summary."
                self.update_summary(initial_summary)

            return self.running_summary

        except Exception as e:
            logging.error(f"Error getting summary: {e}")
            return "This is the first call for this project and there is no running summary."

    def update_summary(self, new_content):
        """
        Update the running summary file in the project's data directory.

        Parameters
        ----------
        new_content : str
            The new summary content to write.
        """
        try:
            data_path = get_project_data_path()
            if data_path is None:
                logging.error("Could not get project data path.")
                return

            summary_file = f"{data_path}/running_summary.txt"
            self.running_summary = new_content

            write_file(summary_file, self.running_summary)

        except Exception as e:
            logging.error(f"Error updating summary: {e}")

    # -------------------------------------------------------------------------
    # User Input and Data Assembly
    # -------------------------------------------------------------------------

    def update_user_input(self, user_input):
        """
        Update the user input text that forms part of the user prompt.
        
        Parameters
        ----------
        user_input : str
            The instructions or query provided by the user.
        """
        self.user_input = user_input

    def add_table_data(self, update_tables, context_tables):
        """
        Add table data and structure information to the system prompt.

        Parameters
        ----------
        update_tables : dict
            Dictionary of table_name: table_data for tables that will be updated.
        context_tables : dict
            Dictionary of table_name: table_data for tables used as context only.
        """
        # Step 1: Identify update vs. context tables
        update_table_names = ', '.join(update_tables.keys())
        context_table_names = ', '.join(context_tables.keys()) if context_tables else "None"
        self.table_data = (
            f"\n\n### Update Only These Tables: {update_table_names} ###"
            f"\n\nThe other tables are provided solely for context: {context_table_names}."
        )

        # Step 2: Add structure info and data for update tables
        for table_name, data in update_tables.items():
            structure_info = self.load_ai_instructions_from_structure(table_name)
            formatted_table_data = json.dumps(data, indent=2)
            self.table_data += (
                f"\n\n--- {table_name} Structure Information ---\n{structure_info}"
                f"\n\n--- Current {table_name} Data ---\n{formatted_table_data}"
            )

        # Step 3: Add context tables if present
        if context_tables:
            for table_name, data in context_tables.items():
                structure_info = self.json_manager.load_ai_instructions_from_structure(table_name)
                formatted_table_data = json.dumps(data, indent=2)
                self.table_data += (
                    f"\n\n--- Context for {table_name} ---\n{structure_info}"
                    f"\n\n--- Context {table_name} Data ---\n{formatted_table_data}"
                )

    def add_running_summary(self, summary):
        """
        Add the running summary to the system prompt.
        
        Parameters
        ----------
        summary : str
            The summary content to add.
        """
        if summary:
            self.summary += f"\n\nRunning Summary of Processed PDF:\n{summary}"

    def add_business_description(self, business_description):
        """
        Add the business description to the system prompt.
        
        Parameters
        ----------
        business_description : str
            The business description text.
        """
        if business_description:
            self.business_description += f"\n\nBusiness Description:\n{business_description}"
        else:
            self.business_description += "\n\nNo business description is given. Please use the PDF information."

    def add_pdf_chunk(self, pdf_chunk):
        """
        Add a chunk of the PDF content to the system prompt.
        
        Parameters
        ----------
        pdf_chunk : str
            The extracted PDF text chunk.
        """
        if pdf_chunk:
            self.pdf_chunk += f"\n\n--- PDF Chunk ---\n{pdf_chunk}"

    def add_chunk_info(self, chunk_num):
        """
        Add information about the current PDF chunk number being processed.
        
        Parameters
        ----------
        chunk_num : int
            The chunk number of the PDF currently being processed.
        """
        self.chunk_num_text += f"\n\n### PDF Processing ###\nCurrently processing chunk {chunk_num} of the PDF."

    # -------------------------------------------------------------------------
    # Prompt Assembly
    # -------------------------------------------------------------------------

    def update_system_prompt_info(self, update_tables=None, context_tables=None, summary=None, business_description=None, pdf_chunk=None, chunk_num=None):
        """
        Update the system prompt information with tables, summaries, business descriptions, and PDF content.

        Parameters
        ----------
        update_tables : dict, optional
        context_tables : dict, optional
        summary : str, optional
        business_description : str, optional
        pdf_chunk : str, optional
        chunk_num : int, optional
        """
        self.reset_prompts()
        if update_tables:
            self.add_table_data(update_tables, context_tables)
        if summary:
            self.add_running_summary(summary)
        if business_description:
            self.add_business_description(business_description)
        if pdf_chunk:
            self.add_pdf_chunk(pdf_chunk)
            self.add_chunk_info(chunk_num)

    def assemble_system_prompt(self):
        """
        Assemble the complete system prompt by concatenating the base prompt and all appended data.
        """
        if not self.static_prompt_text:
            self.load_prompt_file()

        complete_prompt = (
            self.static_prompt_text + "\n\n" +
            self.business_description +
            self.table_data +
            self.summary +
            self.chunk_num_text +
            self.user_prompt
        )

        self.system_prompt = complete_prompt

    def write_system_prompt(self):
        """
        Write the current system prompt to a file in the project's data directory in S3.
        """
        data_path = get_project_data_path()
        if data_path is None:
            logging.error("Could not get project data path for writing system prompt")
            return
            
        s3_path = f"{data_path}/complete_prompt.txt"
        write_file(s3_path, self.system_prompt)

    def get_system_prompt(self):
        """
        Get the assembled system prompt.

        Returns
        -------
        str
            The full system prompt content.
        """
        self.assemble_system_prompt()
        self.write_system_prompt()
        return self.system_prompt

    def get_user_prompt(self):
        """
        Assemble and return the user prompt section (user instructions + PDF chunk).

        Returns
        -------
        str
            The user prompt content.
        """
        if self.user_input:
            self.user_prompt += 'Here are the specific instructions provided by the user:\n' + self.user_input
        else:
            self.user_prompt += "No specific instructions provided by the user.\n"

        if self.pdf_chunk:
            self.user_prompt += "Here is a part of the attached PDF\n" + self.pdf_chunk

        return self.user_prompt

    # -------------------------------------------------------------------------
    # Token Counting and Cost Calculation
    # -------------------------------------------------------------------------

    def get_token_count(self, component):
        """
        Calculate the total token count for a given component of the prompt.

        Parameters
        ----------
        component : str
            'system' or 'user' component to count tokens for.

        Returns
        -------
        int
            The total token count for the specified component.
        """
        total_tokens = 0
        if component == 'system':
            total_tokens += count_tokens(self.system_prompt)
            total_tokens += count_tokens(self.business_description)
            total_tokens += count_tokens(self.table_data)
            total_tokens += count_tokens(self.summary)
        elif component == 'user':
            total_tokens += count_tokens(self.user_prompt)

        return total_tokens

    def display_tokens_and_cost(self, response):
        """
        Display token usage and cost estimates for input and output based on the response.

        Parameters
        ----------
        response : dict
            Contains the "text" key for output token calculation.
        """
        total_input_tokens = self.get_token_count('system') + self.get_token_count('user')
        total_output_tokens = count_tokens(response["text"])
        input_cost = total_input_tokens * OPENAI_COST_PER_INPUT_TOKEN
        output_cost = total_output_tokens * OPENAI_COST_PER_OUTPUT_TOKEN
        total_cost = input_cost + output_cost

        logging.info(f"Total input tokens: {total_input_tokens}, cost: ${input_cost:.4f} USD")
        logging.info(f"Total output tokens: {total_output_tokens}, cost: ${output_cost:.4f} USD")
        logging.info(f"Total cost: ${total_cost:.4f} USD")

    # -------------------------------------------------------------------------
    # Structure and Description Info Loading
    # -------------------------------------------------------------------------

    def load_ai_instructions_from_structure(self, table_name):
        """
        Load only the AI instructions from a table's structure JSON file.
            Parameters
        ----------
        table_name : str
            Name of the table to retrieve AI instructions for.
            Returns
        -------
        str
            The table's AI instructions, or empty string if not found.
        """
        try:
            project_data_path = get_project_data_path()
            if not project_data_path:
                logging.error("Could not get project data path")
                return ""
                
            structure_filename = f"{table_name}_structure.json"
            s3_path = f"{project_data_path}/structures/{structure_filename}"
            
            try:
                structure_data = read_json(s3_path)
            except:
                logging.warning(f"Structure file not found in S3: {s3_path}")
                return ""
                
            root_key = next(iter(structure_data))
            table_info = structure_data[root_key]
            # Extract only the AI instructions
            ai_instructions = []
            
            # Add table-level AI instructions if they exist
            if 'ai_instructions' in table_info:
                ai_instructions.append(f"Table Purpose: {table_info['ai_instructions']}")
            # Extract field-level AI instructions from the structure
            if 'structure' in table_info:
                root_struct_key = next(iter(table_info['structure']))
                properties = table_info['structure'][root_struct_key]['items']['properties']
                
                for field_name, field_info in properties.items():
                    if 'ai_instructions' in field_info:
                        ai_instructions.append(f"{field_name}: {field_info['ai_instructions']}")
            return "\n".join(ai_instructions)
        except Exception as e:
            logging.error(f"Error loading structure info for table {table_name}: {e}")
            return ""