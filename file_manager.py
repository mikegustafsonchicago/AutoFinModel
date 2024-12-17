# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:09:12 2024

@author: mikeg
"""

# file_manager.py
import os
import json
import logging
from config import RUNNING_SUMMARY_FILE, USER_DATA_FOLDER
from context_manager import get_user_context

def ensure_directory_exists(path):
    """Ensure a directory exists, create it if it doesn't."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def read_file(file_path, default=""):
    """Read a file and return its contents. Return a default value if the file does not exist."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    return default

def write_file(file_path, content):
    """Write content to a file, ensuring the directory exists."""
    ensure_directory_exists(file_path)
    with open(file_path, "w") as file:
        file.write(content)

def read_json(file_path):
    """Read a JSON file and return its contents."""
    with open(file_path, "r") as file:
        return json.load(file)

def write_json(file_path, data):
    """Write data to a JSON file."""
    ensure_directory_exists(file_path)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def initialize_session_files(json_manager):
    user_context = get_user_context()
    logging.debug(f"initialize_session_files: Initializing session files for {user_context.username} with project {user_context.current_project} of type {user_context.project_type}")
    data_path = get_project_data_path()
    if data_path is None:
        logging.error("initialize_session_files: data_path is None, cannot initialize files")
        return
    json_manager.initialize_user_json_structures()
    json_manager.initialize_json_files(data_path)
    


def create_new_user():
    """Create the base folder structure for a new user."""
    user_context = get_user_context()
    
    # Create base user directory and user info directory
    user_dir = os.path.join('users', user_context.username)
    user_info_dir = os.path.join(user_dir, 'user_info')
    os.makedirs(user_dir, exist_ok=True)
    os.makedirs(user_info_dir, exist_ok=True)
    
    # Create projects directory
    projects_dir = os.path.join(user_dir, 'projects') 
    os.makedirs(projects_dir, exist_ok=True)
    
    return {
        'user_dir': user_dir,
        'user_info_dir': user_info_dir,
        'projects_dir': projects_dir
    }

def create_new_project(project_name):
    """
    Create a new project folder structure under the user's projects directory.
    
    Args:
        project_name (str): Name of the project to create
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user_context = get_user_context()
        
        # Create project directory structure
        project_base = os.path.join('users', user_context.username, 'projects', project_name)
        project_dirs = [
            os.path.join(project_base, 'data'),
            os.path.join(project_base, 'data', 'structures'),
            os.path.join(project_base, 'uploads'),
            os.path.join(project_base, 'gallery'),
            os.path.join(project_base, 'output')
        ]
        
        # Create each directory
        for directory in project_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logging.debug(f"Created directory: {directory}")
                
        logging.info(f"Successfully created project structure for: {project_name}")
        return True
        
    except Exception as e:
        logging.error(f"Error creating project structure: {str(e)}")
        return False

def list_users():
    """
    List all usernames in the users directory.
    
    Returns:
        list: List of usernames, or empty list if no users found
    """
    try:
        # Check users directory exists
        users_dir = 'users'
        if not os.path.exists(users_dir):
            logging.debug("Users directory does not exist")
            return []
            
        # Get list of directories in users folder
        users = [d for d in os.listdir(users_dir) 
                if os.path.isdir(os.path.join(users_dir, d))]
        
        logging.debug(f"Found {len(users)} users: {users}")
        return users
        
    except Exception as e:
        logging.error(f"Error listing users: {str(e)}")
        return []

def list_projects():
    """
    List all project names in the user's projects folder.
    
    Args:
        username (str): The username to get projects for
        
    Returns:
        list: List of project names, or empty list if no projects found
    """
    try:
        user_context = get_user_context()
        
        # Construct path to user's projects directory 
        projects_dir = os.path.join('users', user_context.username, 'projects')
        
        # Return empty list if directory doesn't exist
        if not os.path.exists(projects_dir):
            logging.debug(f"Projects directory does not exist for user: {user_context.username}")
            return []
            
        # Get list of directories in projects folder
        projects = [d for d in os.listdir(projects_dir) 
                if os.path.isdir(os.path.join(projects_dir, d))]
        
        logging.debug(f"Found {len(projects)} projects for user {user_context.username}: {projects}")
        return projects
        
    except Exception as e:
        logging.error(f"Error listing projects for user {user_context.username}: {str(e)}")
        return []

def get_project_data_contents():
    """Return a list of files in the project's data directory."""
    user_context = get_user_context()
    data_dir = os.path.join('users', user_context.username, user_context.project_type, 'data')
    
    if not os.path.exists(data_dir):
        logging.warning(f"Data directory does not exist for user {user_context.username} and project {user_context.current_project}")
        return []
        
    try:
        files = os.listdir(data_dir)
        return [f for f in files if os.path.isfile(os.path.join(data_dir, f))]
    except Exception as e:
        logging.error(f"Error reading data directory: {str(e)}")
        return []

def get_gallery_contents():
    """Return a list of files in the project's gallery directory."""
    user_context = get_user_context()
    gallery_dir = os.path.join('users', user_context.username, user_context.project_type, 'gallery')
    
    if not os.path.exists(gallery_dir):
        logging.warning(f"Gallery directory does not exist for user {user_context.username} and project {user_context.current_project}")
        return []
        
    try:
        files = os.listdir(gallery_dir)
        return [f for f in files if os.path.isfile(os.path.join(gallery_dir, f))]
    except Exception as e:
        logging.error(f"Error reading gallery directory: {str(e)}")
        return []
    
def get_project_data_path():
    """
    Get the full path to the project's data directory.
    
    Returns:
        str: Full path to the project's data directory
    """
    try:
        user_context = get_user_context()
        data_dir = os.path.join('users', user_context.username, 'projects', user_context.current_project, 'data')
        
        if not os.path.exists(data_dir):
            logging.warning(f"Data directory does not exist for user {user_context.username} and project {user_context.current_project}")
            return None
            
        return data_dir
        
    except Exception as e:
        logging.error(f"Error getting project data path: {str(e)}")
        return None

def get_project_uploads_path():
    """
    Get the full path to the project's uploads directory.
    
    Returns:
        str: Full path to the project's uploads directory
    """
    try:
        user_context = get_user_context()
        uploads_dir = os.path.join('users', user_context.username, 'projects', user_context.current_project, 'uploads')
        
        if not os.path.exists(uploads_dir):
            logging.warning(f"Uploads directory does not exist for user {user_context.username} and project {user_context.current_project}")
            return None
            
        return uploads_dir
        
    except Exception as e:
        logging.error(f"Error getting project uploads path: {str(e)}")
        return None


def get_project_structures_path():
    """
    Get the full path to the project's structures directory.
    
    Returns:
        str: Full path to the project's structures directory
    """
    try:
        user_context = get_user_context()
        structures_dir = os.path.join('users', user_context.username, 'projects', user_context.current_project, 'data', 'structures')
        
        if not os.path.exists(structures_dir):
            logging.warning(f"Structures directory does not exist for user {user_context.username} and project {user_context.current_project}")
            return None
            
        return structures_dir
        
    except Exception as e:
        logging.error(f"Error getting project structures path: {str(e)}")
        return None


def copy_prompt_to_project():
    """
    Copy the appropriate prompt file from static prompts to project data directory.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user_context = get_user_context()
        # Determine source prompt file based on project type
        if user_context.project_type == "financial":
            src_prompt = "prompt.txt"
        elif user_context.project_type == "catalyst":
            src_prompt = "catalyst_prompt.txt" 
        elif user_context.project_type == "real_estate":
            src_prompt = "real_estate_prompt.txt"
        else:
            logging.error(f"Invalid project type: {user_context.project_type}")
            return False

        # Get source and destination paths
        src_path = os.path.join('static', 'prompts', src_prompt)
        dest_path = os.path.join('users', user_context.username, 'projects', user_context.current_project, 'data', src_prompt)

        # Ensure source exists
        if not os.path.exists(src_path):
            logging.error(f"Source prompt file does not exist: {src_path}")
            return False

        # Create destination directory if needed
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Copy the file
        import shutil
        shutil.copy2(src_path, dest_path)
        logging.info(f"Successfully copied prompt file to {dest_path}")
        return True

    except Exception as e:
        logging.error(f"Error copying prompt file: {str(e)}")
        return False

