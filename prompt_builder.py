# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:11:48 2024

@author: mikeg
"""

# prompt_builder.py
import os
import json
from json_manager import load_json_explanation
from file_manager import write_file
from config import RUNNING_SUMMARY_DIR
from pdf_processing import count_tokens  

class PromptBuilder:
    def __init__(self):
        with open('static/prompt.txt', 'r') as file:
            self.system_prompt = file.read().strip()
        
        self.table_data=''
        self.summary=''
        self.pdf_chunk=''
        self.chunk_num_text=''
        self.business_description=''
        self.user_input = ''  #User input is the text the user types in
        self.user_prompt='' #The user prompt is text plus payload contents
    
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
            json_explanation = load_json_explanation(table_name)
            self.table_data += f"\n\n--- {table_name} Structure Information ---\n{json_explanation}"
            formatted_table_data = json.dumps(data, indent=2)
            self.table_data += f"\n\n--- Current {table_name} Data ---\n{formatted_table_data}"
        
        # Step 3: Add context tables if provided
        if context_tables:
            for table_name, data in context_tables.items():
                json_explanation = load_json_explanation(table_name)
                self.table_data += f"\n\n--- Context for {table_name} ---\n{json_explanation}"
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
        self.system_prompt += self.business_description
        self.system_prompt += self.table_data
        self.system_prompt += self.summary
        self.system_prompt += self.chunk_num_text
        self.system_prompt += self.user_prompt
        
        #DEBUG.
        self.write_system_prompt()
    
    def write_system_prompt(self):
        full_prompt_file = os.path.join(RUNNING_SUMMARY_DIR, "complete_prompt.txt")
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

