# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 09:27:46 2024

@author: mikeg
"""
import sys
import os
import json
import logging
from datetime import datetime

from config import STRUCTURE_FILES_DIR, FINANCIALS_TABLE, CATALYST_TABLE, JSON_FOLDER, DEFAULT_PROJECT_NAME
from excel_generation.ingredients_code import Ingredient

class JsonManager:
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.DEBUG,
                          format='%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                          handlers=[logging.StreamHandler()])
        

    def initialize_json_files(self, project_name):
        # Create temp directory if it doesn't exist
        if not os.path.exists(JSON_FOLDER):
            try:
                os.makedirs(JSON_FOLDER)
                logging.info(f"Created directory: {JSON_FOLDER}")
            except Exception as e:
                logging.error(f"Failed to create directory {JSON_FOLDER}: {e}")
                return False
                
        # Delete any existing files
        try:
            for filename in os.listdir(JSON_FOLDER):
                file_path = os.path.join(JSON_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logging.info(f"Deleted existing file: {filename}")
        except Exception as e:
            logging.error(f"Error cleaning directory {JSON_FOLDER}: {e}")
            return False
            
        # Create new files with default content for both project types
        success = True
        
        # Choose which table structure to use based on project name
        if project_name == "catalyst":
            table_structure = CATALYST_TABLE
        elif project_name == "financial":
            table_structure = FINANCIALS_TABLE
        else:
            # Use default project name if provided name doesn't match expected values
            logging.warning(f"Unknown project name '{project_name}', using default: {DEFAULT_PROJECT_NAME}")
            table_structure = CATALYST_TABLE if DEFAULT_PROJECT_NAME == "catalyst" else FINANCIALS_TABLE
        
        # Initialize files based on selected structure
        for table_name, structure_filename in table_structure.items():
            # Load structure file
            structure_path = os.path.join(STRUCTURE_FILES_DIR, structure_filename)
            try:
                with open(structure_path, 'r') as f:
                    structure_data = json.load(f)
                    
                # Get file info from structure
                # The structure files have a top-level key matching the table name
                file_info = structure_data[table_name]
                file_path = os.path.join(JSON_FOLDER, file_info["filename"])
                
                # Create initial data with root key and default content
                initial_data = {}
                initial_data[file_info["root_key"]] = file_info["default_content"][file_info["root_key"]]
                
                # Write the file
                with open(file_path, 'w') as json_file:
                    json.dump(initial_data, json_file, indent=4)
                logging.info(f"Created {project_name} file with default content: {file_info['filename']}")
                
            except Exception as e:
                logging.error(f"Failed to create {file_path}: {e}")
                success = False
            
        return success

    def load_json_data(self, identifier, project_name=DEFAULT_PROJECT_NAME):
        #Step 1. Get the folder location. Use the TABLE in config.py to find the structure file
        table_structure = CATALYST_TABLE if project_name == "catalyst" else FINANCIALS_TABLE
        # Get structure filename and validate
        structure_filename = None
        if identifier in table_structure:
            # Direct match found
            structure_filename = table_structure[identifier]
        else:
            # Search for partial match in table names
            for table_name, filename in table_structure.items():
                if identifier in table_name.lower():
                    structure_filename = filename
                    break
                    
        if not structure_filename:
            logging.error(f"load_json_data: No matching schema found for identifier: {identifier}")
            return None, None
            
        # Stepdef 2 Load structure file to get file info
        structure_path = os.path.join(STRUCTURE_FILES_DIR, structure_filename)
        try:
            with open(structure_path, 'r') as f:
                structure_data = json.load(f)
                # Get the table name from the first key in structure data
                table_name = next(iter(structure_data))
                file_info = structure_data[table_name]
        except Exception as e:
            logging.error(f"load_json_data: Error loading structure file {structure_filename}: {e}")
            return None, None
            
        # Step 3. Use the file info to get the file path and load the data
        file_path = os.path.join(JSON_FOLDER, file_info["filename"])
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                logging.info(f"load_json_data: Successfully loaded data for {identifier}")
        except FileNotFoundError:
            logging.error(f"load_json_data: File not found at path: {file_path}")
            return None, None
        except json.JSONDecodeError as e:
            logging.error(f"load_json_data: JSON parsing error for {file_path}: {e}")
            return None, None
        except Exception as e:
            logging.error(f"load_json_data: Unexpected error loading {file_path}: {e}")
            return None, None

        # Get the root key from file_info
        root_key = file_info.get("root_key")

        # Return the data under the root key
        try:
            # For all tables, return the data under the root key if it exists
            if root_key:
                return data.get(root_key, [])
            return data, root_key
                
        except Exception as e:
            logging.error(f"load_json_data: Error processing data for {identifier}: {e}. Data is {data}")
            return None, None


    def load_json_explanation(self, table_name, project_name=DEFAULT_PROJECT_NAME):
        """Load explanation text for a given table"""
        # Get the appropriate table mapping based on project
        table_mapping = CATALYST_TABLE if project_name == "catalyst" else FINANCIALS_TABLE
        
        # Check if table exists in mapping
        if table_name not in table_mapping:
            logging.error(f"load_json_explanation: Invalid table name: {table_name}")
            return "No explanation available."

        # Get structure filename from mapping
        structure_filename = table_mapping[table_name]
        
        # Load structure file to get explanation filename
        structure_path = os.path.join(STRUCTURE_FILES_DIR, structure_filename)
        try:
            with open(structure_path, 'r') as f:
                structure_data = json.load(f)
                # Get the table name from the first key in structure data
                table_key = next(iter(structure_data))
                explanation_file = structure_data[table_key]["explanation_file"]
        except Exception as e:
            logging.error(f"load_json_explanation: Error loading structure file {structure_filename}: {e}")
            return "No explanation available."

        # Determine project folder
        project_folder = "catalyst" if project_name == "catalyst" else "fin_model"
        
        file_path = os.path.join(STRUCTURE_FILES_DIR, project_folder, explanation_file)
        
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"load_json_explanation: Explanation file not found at path: {file_path}")
            return "No explanation available."
        except Exception as e:
            logging.error(f"load_json_explanation: Error reading explanation file: {e}")
            return "No explanation available."

    def update_json_files(self, json_data, project_name):
        """Update JSON files with new data"""
        # Get the appropriate table mapping based on project
        table_mapping = CATALYST_TABLE if project_name == "catalyst" else FINANCIALS_TABLE
        
        if not table_mapping:
            logging.error(f"update_json_files: No table mapping found for project: {project_name}")
            return
            
        for table_name, new_data in json_data.items():
            # Check if table exists in mapping
            if table_name not in table_mapping:
                logging.warning(f"update_json_files: No mapping found for table: {table_name} in project {project_name}")
                continue
                
            # Get structure filename from mapping
            structure_filename = table_mapping[table_name]
            
            # Load structure file to get filename
            structure_path = os.path.join(STRUCTURE_FILES_DIR, structure_filename)
            try:
                with open(structure_path, 'r') as f:
                    structure_data = json.load(f)
                    # Get the table name from the first key in structure data
                    table_key = next(iter(structure_data))
                    file_name = structure_data[table_key]["filename"]
            except Exception as e:
                logging.error(f"update_json_files: Error loading structure file {structure_filename}: {e}")
                continue

            file_path = os.path.join(JSON_FOLDER, file_name)

            try:
                with open(file_path, "w") as json_file:
                    json.dump(new_data, json_file, indent=4)
                logging.info(f"update_json_files: Successfully updated {file_name} for project {project_name}")
            except Exception as e:
                logging.error(f"update_json_files: Failed to update {file_name} for project {project_name}: {e}")

    def fix_incomplete_json(self, json_string):
        """Fix incomplete JSON by adding missing brackets"""
        open_curly = json_string.count('{')
        close_curly = json_string.count('}')
        open_square = json_string.count('[')
        close_square = json_string.count(']')

        if open_curly > close_curly:
            json_string += '}' * (open_curly - close_curly)
        if open_square > close_square:
            json_string += ']' * (open_square - close_square)

        return json_string

    def save_json_to_file(self, json_data):
        """Save JSON data to a timestamped file"""
        os.makedirs(JSON_FOLDER, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"openai_response_{timestamp}.json"
        file_path = os.path.join(JSON_FOLDER, file_name)

        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

        logging.info(f"save_json_to_file: Saved JSON response to {file_path}")