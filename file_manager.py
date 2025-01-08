# -*- coding: utf-8 -*-
"""
file_manager.py

This module provides helper functions for managing user directories, project
structures, file I/O (read/write JSON and text files), and listing existing
users/projects. It relies on user context information from `context_manager` and
configuration values from `config`. Files are stored in Amazon S3, except for
static files which are hosted locally.

Created on Wed Nov  6 12:09:12 2024
@author: mikeg
"""

import os
import json
import logging
import datetime
from flask import session
import boto3
from botocore.exceptions import ClientError
from config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    BUCKET_NAME
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler('file_manager.log')
file_handler.setLevel(logging.DEBUG)

# Create formatters and add to handlers
console_format = logging.Formatter('%(levelname)s - %(message)s')
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


#==============================================================================
# AWS S3
#==============================================================================
# Setup S3 client with credentials from .env
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_file_to_s3(file_path, s3_path):
    """Upload a file to S3"""
    logger = logging.getLogger(__name__)
    
    try:
        # Verify file exists locally
        if not os.path.exists(file_path):
            logger.error(f"Local file does not exist: {file_path}")
            return False
            
        logger.debug(f"File exists locally, size: {os.path.getsize(file_path)} bytes")
        
        # Attempt upload
        s3_client.upload_file(file_path, BUCKET_NAME, s3_path)
        
        # Verify upload succeeded
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_path)
            logger.debug("Upload verified - file exists in S3")
        except ClientError:
            logger.error("Upload appeared to succeed but file not found in S3")
            return False
            
        return True
        
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        logger.debug(f"Full error details: {e.response['Error']}")
        return False

def upload_to_s3_gallery(local_file_path, gallery_name, file_name):
    """Upload a file to an S3 gallery folder."""
    logger = logging.getLogger(__name__)
    
    try:
        username = session['user']['username']
        current_project = session['current_project']['name']
        
        # Update the path construction to match your S3 structure
        s3_path = f"users/{username}/projects/{current_project}/gallery/{file_name}"
        logger.debug(f"upload_to_s3_gallery: Uploading {file_name} to {s3_path}")
        
        success = upload_file_to_s3(local_file_path, s3_path)
        
        if success:
            logger.info(f"Successfully uploaded {file_name} to gallery {gallery_name}")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error uploading to gallery: {str(e)}")
        return False


def download_file_from_s3(s3_path, local_path):
    """Download a file from S3"""
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3_client.download_file(BUCKET_NAME, s3_path, local_path)
        return True
    except ClientError as e:
        logging.error(f"Error downloading file from S3: {str(e)}")
        return False

def delete_file_from_s3(s3_path):
    """Delete a file from S3"""
    logger = logging.getLogger(__name__)
    
    try:
        # First check if file exists
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_path)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.warning(f"File does not exist in S3: {s3_path}")
                return False
            raise e

        # Delete the file
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_path)
        
        # Verify deletion
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_path)
            logger.error("File still exists after deletion attempt")
            return False
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.info(f"Successfully deleted file: {s3_path}")
                return True
            raise e
            
    except ClientError as e:
        logger.error(f"Error deleting file from S3: {str(e)}")
        logger.debug(f"Full error response: {e.response['Error']}")
        return False

def list_s3_directory_contents(prefix, create_if_missing=True):
    """
    List files in an S3 directory. Optionally create directory if missing.
    Returns:
        - List of filenames (without path prefix)
        - Empty list if directory is empty or on error
    """
    try:
        # First check if directory exists
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=1
        )
        # If directory doesn't exist and we should create it
        if 'Contents' not in response and create_if_missing:
            try:
                s3_client.put_object(Bucket=BUCKET_NAME, Key=prefix)
                logging.info(f"Created directory: {prefix}")
            except ClientError as e:
                logging.error(f"Failed to create directory: {str(e)}")
                return []
        
        # Get all contents
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        files = [
            obj['Key'].split('/')[-1] 
            for obj in response.get('Contents', [])
            if not obj['Key'].endswith('/')
        ]
        
        return files
        
    except ClientError as e:
        logging.error(f"Error accessing directory {prefix}: {str(e)}")
        return []

def get_project_path(path_type):
    """
    Get S3 path for different project directories.
    Args:
        path_type: One of 'data', 'uploads', 'outputs', 'gallery', 'structures'
    Returns:
        Full S3 path or None on error
    """
    try:
        username = session['user']['username']
        current_project = session['current_project']['name']
        
        base_path = f"users/{username}/projects/{current_project}"
        
        paths = {
            'data': f"{base_path}/data",
            'uploads': f"{base_path}/uploads",
            'outputs': f"{base_path}/outputs",
            'gallery': f"{base_path}/gallery",
            'structures': f"{base_path}/data/structures"
        }
        
        if path_type not in paths:
            logging.error(f"Invalid path type requested: {path_type}")
            return None
            
        return paths[path_type]
        
    except Exception as e:
        logging.error(f"Error getting project path: {str(e)}")
        return None

# =============================================================================
# Basic File Operations
# =============================================================================

def read_file(s3_path, default=""):
    """
    Read and return the contents of a file from S3 as a string.
    If the file does not exist, return the specified default value.
    """
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_path)
        return response['Body'].read().decode('utf-8')
    except ClientError:
        return default

def write_file(s3_path, content):
    """Write string content to a file in S3"""
    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_path, Body=content.encode('utf-8'))
        return True
    except ClientError as e:
        logging.error(f"Error writing file to S3: {str(e)}")
        return False

def read_json(s3_path):
    """Read a JSON file from S3 and return its deserialized Python object"""
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_path)
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        logging.error(f"Error reading JSON from S3: {str(e)}")
        raise

def write_json(s3_path, data):
    """Serialize a Python object to JSON and write it to S3"""
    try:
        json_str = json.dumps(data, indent=4)
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_path, Body=json_str.encode('utf-8'))
        return True
    except ClientError as e:
        logging.error(f"Error writing JSON to S3: {str(e)}")
        return False

# =============================================================================
# User and Project Initialization
# =============================================================================

def initialize_session_files(json_manager):
    """Initialize session-specific files and structures in S3"""
    data_path = get_project_data_path()
    if data_path is None:
        logging.error("initialize_session_files: data_path is None, cannot initialize files")
        return

    json_manager.initialize_user_json_structures()
    json_manager.initialize_json_files(data_path)
    success = copy_prompt_to_project()
    if not success:
        logging.error("Failed to copy prompt file during session initialization")

def create_new_user():
    """
    Create new user structure in S3.
    Returns a dictionary of the created paths.
    """
    username = session['user']['username']
    logging.debug(f"create_new_user: username = {username}")
    # Define S3 paths
    user_prefix = f"users/{username}"
    user_info_prefix = f"{user_prefix}/user_info"
    projects_prefix = f"{user_prefix}/projects"
    
    # Create empty marker objects to represent directories
    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=f"{user_prefix}/")
        s3_client.put_object(Bucket=BUCKET_NAME, Key=f"{user_info_prefix}/")
        s3_client.put_object(Bucket=BUCKET_NAME, Key=f"{projects_prefix}/")
        
        return {
            'user_dir': user_prefix,
            'user_info_dir': user_info_prefix,
            'projects_dir': projects_prefix
        }
    except ClientError as e:
        logging.error(f"Error creating user structure in S3: {str(e)}")
        return None

def create_new_project(project_name):
    """Create new project structure in S3"""
    try:
        username = session['user']['username']
        project_base = f"users/{username}/projects/{project_name}"
        
        # Define project directories as S3 prefixes
        project_dirs = [
            f"{project_base}/data/",
            f"{project_base}/data/structures/",
            f"{project_base}/data/ai_responses/",
            f"{project_base}/uploads/",
            f"{project_base}/gallery/",
            f"{project_base}/outputs/"
        ]

        # Create empty objects to represent directories
        for directory in project_dirs:
            s3_client.put_object(Bucket=BUCKET_NAME, Key=directory)
        
        logging.info(f"Successfully created project structure for: {project_name}")
        return True

    except Exception as e:
        logging.error(f"Error creating project structure: {str(e)}")
        return False

# =============================================================================
# Listing Functions (Users, Projects)
# =============================================================================

def list_users():
    """List all users from S3"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix="users/",
            Delimiter="/"
        )
        
        users = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                # Extract username from prefix 'users/username/'
                username = prefix['Prefix'].split('/')[1]
                if username:
                    users.append(username)

        return users

    except ClientError as e:
        logging.error(f"Error listing users: {str(e)}")
        return []

def list_projects():
    """List all projects for current user from S3"""
    try:
        username = session['user']['username']
        prefix = f"users/{username}/projects/"
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=prefix,
            Delimiter="/"
        )
        
        projects = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                project = prefix['Prefix'].split('/')[-2]
                if project:
                    projects.append(project)
                    
        return projects

    except ClientError as e:
        logging.error(f"Error listing projects: {str(e)}")
        return []
    
def get_project_metadata():
    """
    Get project metadata from project_metadata.json
    Returns:
        - Dict containing metadata if file exists and is valid JSON
        - Empty dict if file doesn't exist or has invalid JSON
    """
    try:
        username = session['user']['username']
        current_project = session['current_project']['name']
        metadata_path = f"users/{username}/projects/{current_project}/project_metadata.json"
        
        try:
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=metadata_path)
            metadata = json.loads(response['Body'].read().decode('utf-8'))
            return metadata
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logging.info(f"No metadata file found at {metadata_path}")
            else:
                logging.error(f"Error retrieving project metadata: {str(e)}")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in project metadata file: {str(e)}")
            return {}
            
    except Exception as e:
        logging.error(f"Unexpected error getting project metadata: {str(e)}")
        return {}

# =============================================================================
# Directory Content Retrieval
# =============================================================================

def get_project_data_contents():
    """List files in project's data directory from S3"""
    username = session['user']['username']
    current_project = session['current_project']['name']
    prefix = f"users/{username}/projects/{current_project}/data/"
    
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        if 'Contents' in response:
            return [obj['Key'].split('/')[-1] for obj in response['Contents'] 
                   if not obj['Key'].endswith('/')]
        return []
    except ClientError as e:
        logging.error(f"Error reading data directory: {str(e)}")
        return []
    
def get_available_project_data_tables():
    """
    Get list of JSON data files in project's data directory.
    Returns list of filenames without .json extension.
    """
    try:
        # Get all files in data directory
        all_files = get_project_data_contents()
        
        # Filter for only JSON files and remove extension
        json_files = [f.replace('.json', '') for f in all_files 
                     if f.endswith('.json')]

        return json_files
        
    except Exception as e:
        logging.error(f"Error getting available data tables: {str(e)}")
        return []


def get_gallery_contents():
    """List files in project's gallery directory."""
    gallery_path = get_project_path('gallery')
    if not gallery_path:
        return []
    return list_s3_directory_contents(f"{gallery_path}/")

def get_uploads_contents():
    """List files in project's uploads directory."""
    uploads_path = get_project_path('uploads')
    if not uploads_path:
        return []
    return list_s3_directory_contents(f"{uploads_path}/")

# =============================================================================
# Delete Functions
# =============================================================================

def delete_project(project_name):
    """Delete a project and all its contents from S3"""
    if not project_name:
        raise ValueError("Project name cannot be empty")
        
    username = session['user']['username']
    if not username:
        logging.error("Could not get valid username")
        return False
        
    prefix = f"users/{username}/projects/{project_name}/"
    
    try:
        # List all objects in project
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        
        if 'Contents' not in response:
            logging.warning(f"Project path does not exist: {prefix}")
            return False
            
        # Delete all objects
        for obj in response['Contents']:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            
        logging.info(f"Successfully deleted project: {project_name}")
        return True
        
    except ClientError as e:
        logging.error(f"Error deleting project {project_name}: {str(e)}")
        return False

# =============================================================================
# Path Retrieval Functions
# =============================================================================

def get_project_data_path():
    """Get S3 path to project's data directory"""
    try:
        username = session['user']['username']
        current_project = session['current_project']['name']
        return f"users/{username}/projects/{current_project}/data"
    except Exception as e:
        logging.error(f"Error getting project data path: {str(e)}")
        return None

def get_project_uploads_path():
    """Get S3 path to project's uploads directory"""
    try:
        username = session['user']['username']
        current_project = session['current_project']['name']
        return f"users/{username}/projects/{current_project}/uploads"
    except Exception as e:
        logging.error(f"Error getting project uploads path: {str(e)}")
        return None
    
def get_project_outputs_path():
    """Get S3 path to project's outputs directory"""
    try:
        username = session['user']['username']
        current_project = session['current_project']['name']
        return f"users/{username}/projects/{current_project}/outputs"
    except Exception as e:
        logging.error(f"Error getting project outputs path: {str(e)}")
        return None

def get_project_gallery_path():
    """Get S3 path to project's gallery directory"""
    try:
        username = session['user']['username']
        current_project = session['current_project']['name']
        return f"users/{username}/projects/{current_project}/gallery"
    except Exception as e:
        logging.error(f"Error getting project gallery path: {str(e)}")
        return None

def get_project_structures_path():
    """Get the path to the project's structures directory"""
    try:
        data_path = get_project_data_path()
        if not data_path:
            logging.error("Could not get project data path")
            return None
            
        structures_path = f"{data_path}/structures"
        logging.debug(f"Structures path: {structures_path}")
        return structures_path
        
    except Exception as e:
        logging.error(f"Error getting structures path: {str(e)}")
        return None
    
def get_projects_path():
    """Get S3 path to user's projects directory"""
    try:
        username = session['user']['username']
        return f"users/{username}/projects"
    except Exception as e:
        logging.error(f"Error getting projects path: {str(e)}")
        return None

# =============================================================================
# Prompt File Management
# =============================================================================

def copy_prompt_to_project():
    """Copy prompt file from local static folder to project's data directory in S3"""
    try:
        username = session['user']['username']
        current_project = session['current_project']['name']
        project_type = session['current_project']['type']
        # Determine the source prompt file based on project type
        if project_type == "financial":
            src_prompt = "prompt.txt"
        elif project_type == "catalyst":
            src_prompt = "catalyst_prompt.txt"
        elif project_type == "real_estate":
            src_prompt = "real_estate_prompt.txt"
        elif project_type == "ta_grading":
            src_prompt = "ta_grading_prompt.txt"
        elif project_type == "fund_analysis":
            src_prompt = "fund_analysis_prompt.txt"
        else:
            logging.error(f"Invalid project type: {project_type} - cannot copy prompt")
            return False

        # Read from local static folder
        src_path = os.path.join('static', 'prompts', src_prompt)
        dest_key = f"users/{username}/projects/{current_project}/data/{src_prompt}"

        # Check if source prompt file exists locally
        if not os.path.exists(src_path):
            logging.error(f"Source prompt file does not exist in static folder: {src_path}")
            return False

        # Read local file and upload to S3
        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()
            s3_client.put_object(Bucket=BUCKET_NAME, Key=dest_key, Body=content.encode('utf-8'))
            
        logging.info(f"Successfully copied prompt file from static folder to s3://{BUCKET_NAME}/{dest_key}")
        return True

    except Exception as e:
        logging.error(f"Error copying prompt file: {str(e)}")
        return False
def get_available_structure_files():
    """Get list of structure files."""
    structures_path = get_project_path('structures')
    if not structures_path:
        logger.warning("Could not get structures path")
        return []
        
    files = list_s3_directory_contents(f"{structures_path}/")
    structure_files = [f.replace('.json', '') for f in files if f.endswith('_structure.json')]
    
    return structure_files

def get_user_path(username=None):
    """Get S3 path to user's root directory"""
    try:
        if username is None:
            username = session['user']['username']
        return f"users/{username}"
    except Exception as e:
        logging.error(f"Error getting user path: {str(e)}")
        return None

def ensure_user_exists(username):
    """
    Ensures the user folder structure exists in S3.
    Creates it if it doesn't exist.
    Returns True if the structure exists or was created successfully.
    """
    try:
        user_prefix = f"users/{username}/"
        
        # Check if user folder exists
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=user_prefix)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # User folder doesn't exist, create it
                logging.info(f"Creating new user folder structure for {username}")
                return create_new_user()
            else:
                logging.error(f"Error checking user folder: {str(e)}")
                return False
                
    except Exception as e:
        logging.error(f"Error ensuring user exists: {str(e)}")
        return False

def list_project_data_files(data_path):
    """Lists only data files (not structure files) in the project's data directory."""
    try:
        # Normalize path - remove trailing slash if present
        normalized_path = data_path.rstrip('/') + '/'
        
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=normalized_path,
            Delimiter="/"
        )
        
        # Check both Contents and CommonPrefixes
        files = []
        if 'Contents' in response:
            files = [
                obj['Key'].split('/')[-1]
                for obj in response['Contents']
                if (
                    obj['Key'].endswith('.json') 
                    and not obj['Key'].endswith('_structure.json')
                    and not obj['Key'].endswith('/') 
                )
            ]
            
        logging.debug(f"Found data files: {files}")
        if not files:
            logging.warning(f"No data files found at path: {normalized_path}")
            logging.debug(f"Directory contents: {response.get('CommonPrefixes', [])}")
            
        return files
        
    except ClientError as e:
        logging.error(f"AWS Error listing project data files: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error listing project data files: {str(e)}")
        return []
