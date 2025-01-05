# context_manager.py
# This module manages user context and project state throughout the application.
# It provides functionality for managing user sessions, project data, and file access in S3.

from dataclasses import dataclass
from flask import session
from typing import Optional
import logging
import os
import boto3
from botocore.exceptions import ClientError
from config import ALLOWABLE_PROJECT_TYPES, OUTPUTS_FOR_PROJECT_TYPE
from file_manager import list_projects, get_project_metadata, get_available_structure_files, get_uploads_contents, get_gallery_contents, ensure_user_exists, get_user_path
from datetime import datetime as dt

# Configure S3 client for AWS access
# Uses environment variables for secure credential management
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
)
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')


def initialize_session_context():
    """
    Initializes the context for the current user session.
    Ensures all required session keys exist.
    """
    try:
        # Ensure all required session keys exist
        if 'user' not in session:
            session['user'] = {
                'username': get_or_create_user_id(),
                'is_authenticated': True,
                'portfolio': {
                    'projects': []
                }
            }
        
        # Always ensure current_project exists
        if 'current_project' not in session:
            session['current_project'] = {
                'name': None,
                'type': None,
                'metadata': None,
                'available_tables': [],
                'uploaded_files': [],
                'available_outputs': [],
                'gallery': []
            }
            logging.debug("[initialize_session_context] Created new current_project in session")
        
        if 'application' not in session:
            session['application'] = {
                'available_project_types': ALLOWABLE_PROJECT_TYPES,
                'is_initialized': False
            }
            
        username = session['user']['username']
        
        if not username:
            logging.error("[initialize_session_context] No username found in session")
            raise ValueError("No username found in session")
            
        # Ensure user folder structure exists
        if not ensure_user_exists(username):
            logging.error(f"[initialize_session_context] Failed to create/verify user structure: {username}")
            raise Exception(f"Failed to create or verify user structure for: {username}")
            
        return get_application_context()
        
    except Exception as e:
        logging.error(f"[initialize_session_context] Error initializing session context: {str(e)}")
        raise

def get_application_context():
    """Get the complete application context including user, project, and system data."""
    try:
        # Get fresh list of all projects from S3
        available_projects = list_projects()
        context = {
            'user': get_user_context(available_projects),
            'current_project': get_project_context(),
            'application': get_system_context()
        }
        
        # Update session portfolio to match S3
        session['user']['portfolio']['projects'] = available_projects
        # Format context for readable logging
        context_str = (
            f"\n[get_application_context] Generated context:"
            f"\n  user:"
            f"\n    username: {context['user']['username']}\t\tis_authenticated: {context['user']['is_authenticated']}\t\tprojects: {context['user']['portfolio']['projects']}"
            f"\n  current_project:"
            f"\n    name: {context['current_project']['name']}\t\ttype: {context['current_project']['type']}"
            f"\n    tables: {context['current_project']['available_tables']}"
            f"\n    files: {context['current_project']['uploaded_files']}"
            f"\n    outputs: {context['current_project']['available_outputs']}"
            f"\n    gallery: {context['current_project']['gallery']}"
            f"\n  application:"
            f"\n    project_types: {context['application']['available_project_types']}\t\t initialized: {context['application']['is_initialized']}"
        )
        #logging.debug(context_str)
        return context
        
    except Exception as e:
        logging.error(f"[get_application_context] Error building context: {str(e)}", exc_info=True)
        raise

def get_user_context(available_projects):
    """Get user-specific context including portfolio."""
    # Always get fresh project list from S3 instead of session
    current_projects = list_projects()
    
    return {
        'username': session['user']['username'],
        'is_authenticated': True,
        'portfolio': {
            'projects': current_projects  # Use S3 source of truth
        }
    }

def get_project_context():
    """Get current project context including metadata and available resources."""
    current_project = session['current_project']
    return {
        'name': session['current_project']['name'],
        'type': session['current_project']['type'],
        'metadata': get_project_metadata() if current_project else None,
        'available_tables': get_available_structure_files() or [],
        'uploaded_files': get_uploads_contents(),
        'available_outputs': OUTPUTS_FOR_PROJECT_TYPE.get(session['current_project']['type'], []),
        'gallery': get_gallery_contents() or []
    }

def get_system_context():
    """Get system-wide context including configuration and state."""
    return {
        'available_project_types': ALLOWABLE_PROJECT_TYPES,
        'is_initialized': session['application']['is_initialized']
    }

def get_or_create_user_id():
    """Get existing user ID or create a new one and initialize their context."""
    from datetime import datetime
    import uuid
    from file_manager import ensure_user_exists
    
    if 'user' in session and 'username' in session['user']:
        return session['user']['username']
    
    # Generate new unique ID
    unique_id = f"user_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
    
    # Initialize user session structure
    if 'user' not in session:
        session['user'] = {
            'username': unique_id,
            'is_authenticated': True,
            'portfolio': {
                'projects': []
            }
        }
    else:
        session['user']['username'] = unique_id
    
    # Ensure S3 folder structure exists
    if not ensure_user_exists(unique_id):
        logging.error(f"[get_or_create_user_id] Failed to create S3 structure for: {unique_id}")
        raise Exception("Failed to initialize user storage")
    
    logging.info(f"[get_or_create_user_id] Created new user: {unique_id}")
    return unique_id

def initialize_empty_project_context(project_name, project_type):
    """Initialize context for a new project."""
    logging.debug(f"[initialize_empty_project_context] Starting initialization for project: {project_name}, type: {project_type}")
    
    project_context = {
        'name': project_name,
        'type': project_type,
        'metadata': {
            'created_at': dt.now().isoformat(),
            'last_modified_at': dt.now().isoformat(),
            'project_type': project_type  # Add this to ensure type is stored
        },
        'available_tables': [],
        'uploaded_files': [],
        'available_outputs': OUTPUTS_FOR_PROJECT_TYPE.get(project_type, []),
        'gallery': []
    }
    
    # Update session with new project context
    session['current_project'] = project_context
    logging.debug(f"[initialize_empty_project_context] Updated session project context: {session['current_project']}")
    
    # Don't maintain portfolio in session, just get fresh list when needed
    current_projects = [] #This is empty because we haven't created the project yet
    
    return project_context

def load_project_context(project_name):
    """
    Load context for an existing project.
    Returns the loaded project context dictionary.
    """
    logging.info("[load_project_context] Loading project context")
    
    # Validate project existence
    available_projects = list_projects()
    if project_name not in available_projects:
        raise ValueError(f"Project does not exist: {project_name}")

    # Get metadata
    metadata = get_project_metadata()
    if not metadata:
        raise ValueError("Failed to retrieve project metadata")

    project_type = metadata.get('project_type', 'real_estate')
    
    project_context = {
        'name': project_name,
        'type': project_type,
        'metadata': metadata,
        'available_outputs': OUTPUTS_FOR_PROJECT_TYPE.get(project_type, [])
    }
    
    session['current_project'] = project_context
    
    return project_context



