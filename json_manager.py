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
from file_manager import get_project_data_path, ensure_directory_exists, get_project_structures_path
from config import STRUCTURE_FILES_DIR, FINANCIALS_TABLE, REAL_ESTATE_TABLE, CATALYST_TABLE, DEFAULT_project_type
from excel_generation.ingredients_code import Ingredient
from context_manager import get_user_context

class JsonManager:
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.DEBUG,
                          format='%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                          handlers=[logging.StreamHandler()])
        
    def initialize_json_files(self, data_path):
        """Initialize JSON files with default content based on project type."""
        success = True
        user_context = get_user_context()
        structures_path = get_project_structures_path()
        logging.debug(f"initialize_json_files: Initializing JSON files for {data_path}")

        try:
            # Get all structure files in the structures directory
            structure_files = [f for f in os.listdir(structures_path) if f.endswith('_structure.json')]
            
            for structure_filename in structure_files:
                # Load structure file
                structure_path = os.path.join(structures_path, structure_filename)
                
                try:
                    with open(structure_path, 'r') as f:
                        structure_data = json.load(f)
                        
                    # Get the table name from the first key in structure data
                    table_key = next(iter(structure_data))
                    file_info = structure_data[table_key]
                    
                    # Create output filename by removing _structure from structure filename
                    output_filename = structure_filename.replace('_structure.json', '.json')
                    file_path = os.path.join(data_path, output_filename)
                    
                    # Get default content and root key from structure
                    initial_data = {}
                    initial_data[file_info["root_key"]] = file_info["default_content"][file_info["root_key"]]
                    
                    # Write the file
                    with open(file_path, 'w') as json_file:
                        json.dump(initial_data, json_file, indent=4)
                    logging.info(f"Created file with default content: {output_filename}")
                    
                except Exception as e:
                    logging.error(f"Failed to process structure file {structure_filename}: {e}")
                    success = False
                    
        except Exception as e:
            logging.error(f"Failed to initialize JSON files: {e}")
            success = False
            
        return success
    
    def load_json_data(self, table_identifier):
        """
        Load JSON data for a specific table in a project.
        
        Args:
            table_identifier (str): The name or identifier of the table to load (e.g. 'expenses', 'revenue', etc.)
            
        Returns:
            list: The loaded JSON data as a list of records
        """
        project_data_path = get_project_data_path()
        
        # Directly construct file path from table identifier
        file_path = os.path.join(project_data_path, f"{table_identifier}.json")
        
        try:
            with open(file_path, 'r') as file:
                table_data = json.load(file)
                
                # If data is a dict with a single key containing a list, return the list
                if isinstance(table_data, dict) and len(table_data) == 1:
                    return list(table_data.values())[0]
                
                # Otherwise return the data as-is (should be a list)
                return table_data
                    
        except FileNotFoundError:
            logging.error(f"load_json_data: File not found at path: {file_path}")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"load_json_data: JSON parsing error for {file_path}: {e}")
            return []
        except Exception as e:
            logging.error(f"load_json_data: Unexpected error loading {file_path}: {e}")
            return []
        
    
    def initialize_user_json_structures(self):
        """
        Copy JSON structure files from static folder to project structure folder.
            
        Returns:
            bool: True if all files copied successfully, False if any errors occurred
        """
        user_context = get_user_context()
        # Get structure files list based on project type
        if user_context.project_type == "catalyst":
            structure_files = CATALYST_TABLE
        elif user_context.project_type == "real_estate":
            structure_files = REAL_ESTATE_TABLE
        elif user_context.project_type == "financial":
            structure_files = FINANCIALS_TABLE
        else:
            logging.error(f"initialize_user_json_structures: Invalid project type: {user_context.project_type}")
            return False

        # Create destination structure directory if it doesn't exist
        dest_dir = os.path.join('users', user_context.username, 'projects', 
                               user_context.current_project, 'data', 'structures')
        os.makedirs(dest_dir, exist_ok=True)

        # Copy structure files
        success = True
        for structure_file in structure_files:
            try:
                # Copy structure file
                source_file = os.path.join(STRUCTURE_FILES_DIR, structure_file)
                dest_file = os.path.join(dest_dir, structure_file)
                
                if os.path.exists(source_file):
                    with open(source_file, 'r') as src, open(dest_file, 'w') as dst:
                        dst.write(src.read())
                    logging.info(f"initialize_user_json_structures: Copied structure file {structure_file}")
                else:
                    logging.warning(f"initialize_user_json_structures: Source structure file not found: {source_file}")
                    success = False

            except Exception as e:
                logging.error(f"initialize_user_json_structures: Error copying structure file {structure_file}: {e}")
                success = False

        return success


    def update_json_files(self, json_data):
        """
        Update JSON files with the complete json data from the openai response. This is called once per openai response.
        """
        user_context = get_user_context()
        project_data_path = get_project_data_path()
        logging.debug(f"update_json_files: Updating JSON files for project {user_context.project_type} with data: {json_data}\n Project data path: {project_data_path}")
        
        # Get list of existing table files in data directory
        existing_tables = []
        if os.path.exists(project_data_path):
            existing_tables = [f.replace('.json', '') for f in os.listdir(project_data_path)
                             if os.path.isfile(os.path.join(project_data_path, f)) and f.endswith('.json')]
            
        for table_name, new_data in json_data.items():
            # Check if table exists in project data directory
            if table_name not in existing_tables:
                logging.warning(f"update_json_files: Table {table_name} not found in project data directory")
                continue

            # Construct filename from table name
            file_name = f"{table_name}.json"
            file_path = os.path.join(project_data_path, file_name)

            try:
                with open(file_path, "w") as json_file:
                    json.dump(new_data, json_file, indent=4)
                logging.info(f"update_json_files: Successfully updated {file_name} for project {user_context.project_type}")
            except Exception as e:
                logging.error(f"update_json_files: Failed to update {file_name} for project {user_context.project_type}: {e}")

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
        user_context = get_user_context()
        project_data_path = get_project_data_path()

        """Save JSON data to a timestamped file"""
        os.makedirs(project_data_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"openai_response_{timestamp}.json"
        file_path = os.path.join(project_data_path, file_name)

        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

        logging.info(f"save_json_to_file: Saved JSON response to {file_path}")


    def get_table_schema(self, table_name):
        """
        Get the schema (structure) of a given table.
        The schema defines the columns and their properties.
        
        Args:
            table_name (str): Name of the table to get schema for
            
        Returns:
            dict: The schema if found, None if not found
        """

        try:
            structures_path = get_project_structures_path()
            
            # Load structure file for table
            structure_file = os.path.join(structures_path, f"{table_name}_structure.json")
            
            if os.path.exists(structure_file):
                logging.debug(f"get_table_schema: Structure file found for {table_name}")
                with open(structure_file, 'r') as f:
                    structure_data = json.load(f)
                    # Get just the structure field value
                    schema = {"structure": structure_data[table_name].get('structure')}
                    if schema["structure"]:
                        return schema
                    logging.debug(f"get_table_schema: No schema found in structure data for {table_name}")
            else:
                logging.debug(f"get_table_schema: No structure file found for {table_name}")
            
            return None
            
        except Exception as e:
            logging.error(f"Error retrieving schema for {table_name}: {str(e)}", exc_info=True)
            return None