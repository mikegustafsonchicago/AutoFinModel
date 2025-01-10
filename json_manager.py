# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 09:27:46 2024

@author: mikeg
"""

import os
import json
import logging
from datetime import datetime
from file_manager import (
    get_project_data_path, get_project_structures_path,
    read_json, write_json, read_file, write_file, 
    upload_file_to_s3, download_file_from_s3,
    s3_client, BUCKET_NAME
)
from config import (
    STRUCTURE_FILES_DIR, 
    FINANCIALS_TABLE, REAL_ESTATE_TABLE, CATALYST_TABLE, FUND_ANALYSIS_TABLE, DEFAULT_PROJECT_METADATA,
    OUTPUTS_FOR_PROJECT_TYPE, TA_GRADING_TABLE
)
from excel_generation.ingredients_code import Ingredient
from flask import session


class JsonManager:
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.DEBUG,
                          format='%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                          handlers=[logging.StreamHandler()])
        
    def initialize_json_files(self, data_path):
        """Initialize JSON structure and data files with default content based on project type."""
        success = True
        username = session.get('username')
        current_project = session.get('current_project')
        structures_path = get_project_structures_path()
        logging.debug(f"initialize_json_files: Initializing JSON files for {data_path}")

        try:
            # List structure files in S3
            response = s3_client.list_objects_v2(
                Bucket=BUCKET_NAME,
                Prefix=f"{structures_path}/"
            )
            
            if 'Contents' not in response:
                logging.error("No structure files found in S3")
                return False

            # Filter for structure files
            structure_files = [obj['Key'] for obj in response['Contents'] 
                             if obj['Key'].endswith('_structure.json')]
            
            for structure_path in structure_files:
                try:
                    # Read structure file from S3
                    structure_data = read_json(structure_path)
                    
                    # Get the table name from the first key in structure data
                    table_key = next(iter(structure_data))
                    file_info = structure_data[table_key]
                    
                    # Create output S3 path by removing _structure from structure filename
                    output_filename = structure_path.split('/')[-1].replace('_structure.json', '.json')
                    output_path = f"{data_path}/{output_filename}"
                    
                    # Get default content and root key from structure
                    initial_data = {}
                    initial_data[file_info["root_key"]] = file_info["default_content"][file_info["root_key"]]
                    
                    # Write directly to S3
                    write_json(output_path, initial_data)
                    logging.info(f"Created file with default content in S3: {output_path}")
                    
                except Exception as e:
                    logging.error(f"Failed to process structure file {structure_path}: {e}")
                    success = False
            
            # Create project metadata in S3
            project_path = '/'.join(data_path.split('/')[:-1])  # Get parent path in S3
            project_type = session.get('project_type')
            self.create_project_metadata(project_path, project_type)
            
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
        file_path = f"{project_data_path}/{table_identifier}.json"
        
        try:
            table_data = read_json(file_path)
            
            # If data is a dict with a single key containing a list, return the list
            if isinstance(table_data, dict) and len(table_data) == 1:
                return list(table_data.values())[0]
            
            # Otherwise return the data as-is (should be a list)
            return table_data
                
        except Exception as e:
            logging.error(f"load_json_data: Error loading {file_path}: {e}")
            return []
    
    def initialize_user_json_structures(self):
        """
        Copy JSON structure files from static folder to project structure folder in S3.
            
        Returns:
            bool: True if all files copied successfully, False if any errors occurred
        """
        logging.debug("[initialize_user_json_structures] Starting initialize_user_json_structures")
        
        username = session['user']['username']
        current_project = session['current_project']['name']
        project_type = session['current_project']['type']
        
        logging.debug(f"[initialize_user_json_structures] User: {username}, Project: {current_project}, Type: {project_type}")

        # Get structure files list based on project type
        if project_type == "catalyst":
            structure_files = CATALYST_TABLE
            logging.debug(f"Using CATALYST_TABLE with {len(CATALYST_TABLE)} files")
        elif project_type == "real_estate":
            structure_files = REAL_ESTATE_TABLE
            logging.debug(f"Using REAL_ESTATE_TABLE with {len(REAL_ESTATE_TABLE)} files")
        elif project_type == "financial":
            structure_files = FINANCIALS_TABLE
            logging.debug(f"Using FINANCIALS_TABLE with {len(FINANCIALS_TABLE)} files")
        elif project_type == "ta_grading":
            structure_files = TA_GRADING_TABLE
            logging.debug(f"Using TA_GRADING_TABLE with {len(TA_GRADING_TABLE)} files")
        elif project_type == "fund_analysis":
            structure_files = FUND_ANALYSIS_TABLE
            logging.debug(f"Using FUND_ANALYSIS_TABLE with {len(FUND_ANALYSIS_TABLE)} files")
        else:
            logging.error(f"initialize_user_json_structures: Invalid project type: {project_type}")
            return False

        structures_path = get_project_structures_path()
        logging.debug(f"Structures path: {structures_path}")
        success = True
        
        # Copy structure files from local static folder to S3
        logging.debug(f"Starting copy of {len(structure_files)} structure files")
        for structure_file in structure_files:
            try:
                source_file = f"static/json_structure_data/{structure_file}"
                dest_key = f"{structures_path}/{structure_file}"
                
                logging.debug(f"Processing file: {structure_file}")
                logging.debug(f"Source: {source_file}")
                logging.debug(f"Destination: {dest_key}")
                
                # Check if source file exists
                if not os.path.exists(source_file):
                    logging.error(f"Source file does not exist: {source_file}")
                    success = False
                    continue
                
                # Upload file to S3
                success = upload_file_to_s3(source_file, dest_key)
                if success:
                    logging.info(f"Successfully copied structure file {structure_file}")
                else:
                    logging.warning(f"Failed to copy structure file {structure_file}")
                    success = False

            except Exception as e:
                logging.error(f"Error copying structure file {structure_file}: {str(e)}", exc_info=True)
                success = False

        logging.debug(f"initialize_user_json_structures completed with success={success}")
        return success

    def update_json_files(self, json_data):
        """
        Update JSON files with the complete json data from the openai response. This is called once per openai response.
        """
        username = session.get('username')
        current_project = session.get('current_project')
        project_type = session.get('project_type')
        project_data_path = get_project_data_path()
        
        # List existing files in S3 data directory
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=f"{project_data_path}/"
        )
        
        existing_tables = []
        if 'Contents' in response:
            existing_tables = [
                obj['Key'].split('/')[-1].replace('.json', '')
                for obj in response['Contents']
                if obj['Key'].endswith('.json')
            ]
            
        for table_name, new_data in json_data.items():
            # Check if table exists in project data directory
            if table_name not in existing_tables:
                logging.warning(f"update_json_files: Table {table_name} not found in project data directory")
                continue

            # Write updated data to S3
            file_path = f"{project_data_path}/{table_name}.json"
            try:
                write_json(file_path, new_data)
                logging.info(f"update_json_files: Successfully updated {table_name}.json for project {project_type}")
            except Exception as e:
                logging.error(f"update_json_files: Failed to update {table_name}.json for project {project_type}: {e}")

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
        """Save JSON data to a timestamped file in S3"""
        username = session.get('username')
        current_project = session.get('current_project')
        project_data_path = get_project_data_path()
        save_directory = f"{project_data_path}/ai_responses"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"openai_response_{timestamp}.json"
        file_path = f"{save_directory}/{file_name}"

        try:
            write_json(file_path, json_data)
            logging.info(f"save_json_to_file: Saved JSON response to {file_path}")
        except Exception as e:
            logging.error(f"save_json_to_file: Failed to save JSON response: {e}")

    def get_table_schema(self, table_name):
        """
        Get the schema (structure) and display settings of a given table from S3.
        The schema defines the columns and their properties.
        
        Args:
            table_name (str): Name of the table to get schema for
            
        Returns:
            dict: The schema and display settings if found, None if not found
        """
        try:
            structures_path = get_project_structures_path()
            structure_path = f"{structures_path}/{table_name}_structure.json"
            
            try:
                structure_data = read_json(structure_path)
                table_data = structure_data[table_name]
                
                schema = {
                    "structure": table_data.get('structure'),
                    "display": table_data.get('display')
                }
                
                if schema["structure"]:
                    return schema
                
            except KeyError:
                pass
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            logging.error(f"[get_table_schema] Error retrieving schema for {table_name}: {str(e)}", exc_info=True)
            return None

    def create_project_metadata(self, project_base, project_type):
        """
        Create a metadata JSON file for the project in S3 containing project information.
        
        Args:
            project_base: Base directory path of the project
            project_type: Type of project (financial, real_estate, etc.)
            
        Returns:
            bool: True if metadata was created successfully, False otherwise
        """
        try:
            current_time = datetime.now().isoformat()
            username = session.get('username')
            
            # Start with default metadata from config
            metadata = DEFAULT_PROJECT_METADATA.copy()
            
            # Update dynamic fields
            metadata["project_type"] = project_type
            metadata["created_at"] = current_time 
            metadata["last_modified_at"] = current_time
            metadata["project_owner"] = username
            metadata["collaborators"] = [username]
            metadata["access_level"] = {
                username: "admin"
            }
            
            metadata_path = f"{project_base}/project_metadata.json"
            write_json(metadata_path, metadata)
            logging.debug(f"Created project metadata at: {metadata_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error creating project metadata: {str(e)}")
            return False

    def update_metadata_field(self, field, value):
        """
        Update a specific field in the project metadata.
        
        Args:
            field: The metadata field to update
            value: The new value for the field
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            username = session.get('username')
            current_project = session.get('current_project')
            metadata_path = f"users/{username}/projects/{current_project}/project_metadata.json"
            
            # Read existing metadata
            metadata = read_json(metadata_path)
            if not metadata:
                logging.error("Could not read existing metadata")
                return False
            
            # Validate field exists in default schema
            if field not in DEFAULT_PROJECT_METADATA:
                logging.error(f"Invalid metadata field: {field}")
                return False
            
            # Update the specified field
            metadata[field] = value
            
            # Always update last_modified_at when metadata changes
            metadata["last_modified_at"] = datetime.now().isoformat()
            
            # Write back to S3
            success = write_json(metadata_path, metadata)
            if success:
                logging.info(f"Successfully updated metadata field: {field}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error updating metadata field {field}: {str(e)}")
            return False

    def increment_file_count(self, increment=1):
        """
        Increment or decrement the file count in project metadata.
        
        Args:
            increment: Number to add to file count (negative to decrease)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            username = session.get('username')
            current_project = session.get('current_project')
            metadata_path = f"users/{username}/projects/{current_project}/project_metadata.json"
            
            metadata = read_json(metadata_path)
            if not metadata:
                return False
            
            current_count = metadata.get("file_count", 0)
            metadata["file_count"] = max(0, current_count + increment)  # Prevent negative count
            metadata["last_modified_at"] = datetime.now().isoformat()
            
            return write_json(metadata_path, metadata)
            
        except Exception as e:
            logging.error(f"Error updating file count: {str(e)}")
            return False

    def update_last_output(self, output_type):
        """
        Update the last_output_generated timestamp and type.
        Validates output type against allowed outputs for project type.
        
        Args:
            output_type: Type of output generated (excel_model, powerpoint_overview, etc.)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            project_type = session.get('project_type')
            
            # Validate output type is allowed for this project type
            if output_type not in OUTPUTS_FOR_PROJECT_TYPE.get(project_type, []):
                logging.error(f"Invalid output type {output_type} for project type {project_type}")
                return False
                
            return self.update_metadata_field("last_output_generated", {
                "timestamp": datetime.now().isoformat(),
                "type": output_type
            })
        except Exception as e:
            logging.error(f"Error updating last output: {str(e)}")
            return False