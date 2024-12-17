# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:11:48 2024

@author: mikeg
"""

# prompt_builder.py
import os
import json
import logging
from json_manager import JsonManager
from file_manager import write_file, get_project_data_path, copy_prompt_to_project
from config import OPENAI_COST_PER_INPUT_TOKEN, OPENAI_COST_PER_OUTPUT_TOKEN, BASE_PROMPT_DIR
from pdf_processing import count_tokens  
from context_manager import get_user_context


class PromptBuilder:
    def __init__(self, json_manager):
        self.json_manager = json_manager
        self.system_prompt = ''
        self.project_type = None
        self.table_data = ''
        self.summary = ''
        self.pdf_chunk = ''
        self.chunk_num_text = ''
        self.business_description = ''
        self.user_input = ''  # User input is the text the user types in
        self.user_prompt = '' # The user prompt is text plus payload contents
        self.running_summary = ''

    def load_prompt_file(self):
        """Load the appropriate prompt file based on project type"""
        context = get_user_context()
        self.project_type = context.project_type
        prompt_path = get_project_data_path()

        # Determine prompt filename based on project type
        if context.project_type == "financial":
            prompt_filename = "prompt.txt"
        elif context.project_type == "catalyst":
            prompt_filename = "catalyst_prompt.txt"
        elif context.project_type == "real_estate":
            prompt_filename = "real_estate_prompt.txt"
        else:
            logging.error(f"Error: Invalid project type: {context.project_type}")
            raise ValueError(f"Invalid project type: {context.project_type}")
            
        prompt_file = os.path.join(prompt_path, prompt_filename)
        
        # Copy prompt file if it doesn't exist
        if not os.path.exists(prompt_file):
            success = copy_prompt_to_project()
            if not success:
                # If copy fails, initialize base system prompt instead
                logging.error(f"Failed to copy prompt file for project type: {context.project_type}, initializing base system prompt instead.")
                self.initialize_base_system_prompt()
                return
                
        # Read the prompt file
        with open(prompt_file, 'r') as file:
            self.system_prompt = file.read().strip()
    
    def reset_prompts(self):
        """Reset all prompt components to prevent accumulation"""
        self.table_data = ''
        self.summary = ''
        self.pdf_chunk = ''
        self.chunk_num_text = ''
        self.business_description = ''
        self.user_input = ''
        self.user_prompt = ''
        self.running_summary = "This is the first call for this project and there is no running summary."
        
    def get_summary(self):
        """Get the running summary from the project's data directory."""
        try:
            # Get path to project data directory
            data_path = get_project_data_path()
            if data_path is None:
                logging.error("Could not get project data path")
                return "This is the first call for this project and there is no running summary."

            # Construct path to running summary file
            summary_file = os.path.join(data_path, 'running_summary.txt')

            # Load existing summary if file exists
            if os.path.exists(summary_file):
                with open(summary_file, "r") as file:
                    self.running_summary = file.read()
            else:
                # Initialize new summary and write it
                initial_summary = "This is the first call for this project and there is no running summary."
                self.update_summary(initial_summary)

            return self.running_summary

        except Exception as e:
            logging.error(f"Error getting summary: {str(e)}")
            return "This is the first call for this project and there is no running summary."

    def update_summary(self, new_content):
        """Update the running summary in the project's data directory."""
        try:
            # Get path to project data directory
            data_path = get_project_data_path()
            if data_path is None:
                logging.error("Could not get project data path")
                return

            # Construct path to running summary file
            summary_file = os.path.join(data_path, 'running_summary.txt')

            # Update the running summary content
            self.running_summary = new_content
            logging.debug(f"Updating summary file with content:\n{self.running_summary}")

            # Write updated content to file
            with open(summary_file, "w") as file:
                file.write(self.running_summary)

        except Exception as e:
            logging.error(f"Error updating summary: {str(e)}")
    
    def update_user_input(self,user_input):
        self.user_input = user_input

    def add_table_data(self, update_tables, context_tables):
        # Step 1: Specify tables for updates vs. context
        update_table_names = ', '.join(update_tables.keys())
        context_table_names = ', '.join(context_tables.keys()) if context_tables else "None"
        self.table_data = f"\n\n### Update Only These Tables: {update_table_names} ###"
        self.table_data += f"\n\nThe other tables are provided solely for context: {context_table_names}."
        
        # Step 2: Add table structure info and data for update tables
        for table_name, data in update_tables.items():
            structure_info = self.load_structure_and_description_info(table_name)
            self.table_data += f"\n\n--- {table_name} Structure Information ---\n{structure_info}"
            formatted_table_data = json.dumps(data, indent=2)
            self.table_data += f"\n\n--- Current {table_name} Data ---\n{formatted_table_data}"
        
        # Step 3: Add context tables if provided
        if context_tables:
            for table_name, data in context_tables.items():
                structure_info = self.json_manager.load_structure_and_description_info(table_name)
                self.table_data += f"\n\n--- Context for {table_name} ---\n{structure_info}"
                formatted_table_data = json.dumps(data, indent=2)
                self.table_data += f"\n\n--- Context {table_name} Data ---\n{formatted_table_data}"

    def add_running_summary(self, summary):
        if summary:
            self.summary += f"\n\nRunning Summary of Processed PDF:\n{summary}"

    def add_business_description(self, business_description):
        # Step 6: Include the business description
        if business_description:
            self.business_description += f"\n\nBusiness Description:\n{business_description}"
        else:
            self.business_description += f"\n\nNo business description is given. Please use the information in the pdf to understand the business.\n"

    def add_pdf_chunk(self, pdf_chunk):
        if pdf_chunk:
            self.pdf_chunk += f"\n\n--- PDF Chunk ---\n{pdf_chunk}"
            
    def add_chunk_info(self, chunk_num):
         self.chunk_num_text += f"\n\n### PDF Processing ###\nCurrently processing chunk {chunk_num} of the PDF."
    
    def get_system_prompt(self):
        self.assemble_system_prompt()
        self.write_system_prompt()
        return self.system_prompt
    
    def update_system_prompt_info(self, update_tables=None, context_tables=None, summary=None, business_description=None, pdf_chunk=None, chunk_num=None):
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
        # First load the base prompt if not already loaded
        if not self.system_prompt:
            self.load_prompt_file()
        
        # Create a complete prompt by combining base prompt with other components
        complete_prompt = self.system_prompt + "\n\n"  # Start with base prompt
        complete_prompt += self.business_description
        complete_prompt += self.table_data
        complete_prompt += self.summary
        complete_prompt += self.chunk_num_text
        complete_prompt += self.user_prompt
        
        # Update system_prompt with complete version
        self.system_prompt = complete_prompt
    
    def write_system_prompt(self):
        """Write system prompt to the project's data directory."""
        context = get_user_context()
        # Get the path to the project's data directory
        data_dir = os.path.join('users', context.username, 'projects', context.current_project, 'data')
        
        # Create the full path for the complete prompt file
        full_prompt_file = os.path.join(data_dir, "complete_prompt.txt")
        
        # Write the file (using existing write_file function which handles directory creation)
        write_file(full_prompt_file, self.system_prompt)


    def get_user_prompt(self):
        # Add user input if available, or indicate no additional instructions
        if self.user_input:
            self.user_prompt += 'Here are the specific instructions provided by the user:\n'
            self.user_prompt += self.user_input
        else:
            self.user_prompt += "No specific instructions provided by the user.\n"
        
        if self.pdf_chunk:
            self.user_prompt += "Here is a part of the attached PDF\n"
            self.user_prompt += self.pdf_chunk
        
        return self.user_prompt
    
    def get_token_count(self, component):
        """Calculate total token count for the given component."""
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
        total_input_tokens = self.get_token_count('system') + self.get_token_count('user')
        total_output_tokens = count_tokens(response["text"])
        input_cost = total_input_tokens * OPENAI_COST_PER_INPUT_TOKEN
        output_cost = total_output_tokens * OPENAI_COST_PER_OUTPUT_TOKEN
        total_cost = input_cost + output_cost
        
        logging.info(f"Total input tokens: {total_input_tokens}, cost: ${input_cost:.4f} USD")
        logging.info(f"Total output tokens: {total_output_tokens}, cost: ${output_cost:.4f} USD") 
        logging.info(f"Total cost: ${total_cost:.4f} USD")


    def initialize_base_system_prompt(self):
        """
        Copy system prompt file from static folder to project data folder.
        """
        context = get_user_context()
        # Get source and destination paths based on project type
        if context.project_type == "catalyst":
            source_file = os.path.join(BASE_PROMPT_DIR, "catalyst_prompt.txt")
            dest_filename = "catalyst_prompt.txt"
        elif context.project_type == "real_estate":
            source_file = os.path.join(BASE_PROMPT_DIR, "real_estate_prompt.txt")
            dest_filename = "real_estate_prompt.txt"
        elif context.project_type == "financial":
            source_file = os.path.join(BASE_PROMPT_DIR, "prompt.txt")
            dest_filename = "prompt.txt"
        else:
            logging.error(f"Invalid project type: {context.project_type}")
            return False

        # Create destination directory if it doesn't exist
        dest_dir = os.path.join('users', context.username, 'projects',
                               context.current_project, 'data')
        os.makedirs(dest_dir, exist_ok=True)

        # Copy prompt file
        dest_file = os.path.join(dest_dir, dest_filename)
        try:
            if os.path.exists(source_file):
                with open(source_file, 'r') as src, open(dest_file, 'w') as dst:
                    dst.write(src.read())
                logging.info(f"Copied system prompt file {dest_filename}")
                return True
            else:
                logging.warning(f"Source prompt file not found: {source_file}")
                return False
        except Exception as e:
            logging.error(f"Error copying system prompt file: {e}")
            return False
        

    def load_structure_and_description_info(self, table_name):
        """
        Load and return the structure information for a given table from its JSON structure file.
        
        Args:
            table_name (str): Name of the table to get structure info for
            
        Returns:
            str: Structure information string, or empty string if not found
        """
        try:
            # Load structure file
            structure_filename = f"{table_name}_structure.json"
            project_data_path = get_project_data_path()
            structure_path = os.path.join(project_data_path, 'structures', structure_filename)
            if not os.path.exists(structure_path):
                logging.warning(f"Structure file not found: {structure_path}")
                return ""
                
            with open(structure_path, 'r') as f:
                structure_data = json.load(f)
                
            # Get the root key (first key in structure data)
            root_key = next(iter(structure_data))
            
            # Extract relevant structure information
            table_info = structure_data[root_key]
            description = table_info.get('description', '')
            structure_details = json.dumps(table_info.get('structure', {}), indent=2)
            
            # Format the information
            info_text = f"Description: {description}\n\nStructure:\n{structure_details}"
            
            return info_text

        except Exception as e:
            logging.error(f"Error loading structure info for table {table_name}: {str(e)}")
            return ""

