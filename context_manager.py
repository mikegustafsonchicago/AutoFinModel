# context_manager.py
from dataclasses import dataclass
from flask import session
from typing import Optional
import logging
import os
import boto3
from botocore.exceptions import ClientError
from config import ALLOWABLE_PROJECT_TYPES, OUTPUTS_FOR_PROJECT_TYPE

# Configure S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
)
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# File management helper functions
def list_files_in_s3(prefix):
    """List files in S3 with given prefix"""
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except ClientError as e:
        logging.error(f"Error listing files in S3: {str(e)}")
        return []

def get_project_structures_path():
    """Get S3 path to project's structures directory"""
    try:
        username = session.get('username', 'default')
        current_project = session.get('current_project')
        return f"users/{username}/projects/{current_project}/data/structures"
    except Exception as e:
        logging.error(f"Error getting project structures path: {str(e)}")
        return None

def get_project_uploads_path():
    """Get S3 path to project's uploads directory"""
    try:
        username = session.get('username', 'default')
        current_project = session.get('current_project')
        return f"users/{username}/projects/{current_project}/uploads"
    except Exception as e:
        logging.error(f"Error getting project uploads path: {str(e)}")
        return None

def list_projects():
    """List all projects for current user from S3"""
    try:
        username = session.get('username', 'default')
        prefix = f"users/{username}/projects/"
        
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=prefix,
            Delimiter="/"
        )
        
        projects = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                # Extract project name from prefix
                project = prefix['Prefix'].split('/')[-2]
                if project:
                    projects.append(project)
                    
        return projects

    except ClientError as e:
        logging.error(f"Error listing projects: {str(e)}")
        return []

@dataclass
class UserContext:
    username: str
    current_project: Optional[str] = None
    project_type: Optional[str] = None
    available_projects: list[str] = None
    available_tables: list[str] = None
    new_project_types = ALLOWABLE_PROJECT_TYPES
    uploaded_files: list[str] = None
    available_outputs: list[str] = None

class ContextManager:
    _instance = None  # Class variable to store the singleton instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            username = session.get('username', 'default')  # Get from session or use default
            cls._instance = UserContext(username=username)
            logging.info(f"Created new context instance - username: {username}, project: {cls._instance.current_project}, type: {cls._instance.project_type}, available_projects: {cls._instance.available_projects}, available_tables: {cls._instance.available_tables}")
        cls._instance.current_project = session.get('current_project')
        cls._instance.project_type = session.get('project_type')
        cls._instance.available_projects = session.get('available_projects', [])
        cls._instance.available_tables = session.get('available_tables', [])
        cls._instance.available_outputs = session.get('available_outputs', [])

        return cls._instance

    @staticmethod
    def initialize_session(username):
        old_username = session.get('username')
        if old_username != username:
            logging.info(f"Username changed from {old_username} to {username}")
        session['username'] = username
        
        old_projects = session.get('available_projects', [])
        if old_projects != []:
            logging.info(f"Available projects reset from {old_projects} to []")
        session['available_projects'] = []
        session['available_tables'] = []
        session['available_outputs'] = []

    @staticmethod
    def set_project_context(project_name, project_type):
        old_project = session.get('current_project')
        old_type = session.get('project_type')
        
        if old_project != project_name:
            logging.info(f"Current project changed from {old_project} to {project_name}")
        if old_type != project_type:
            logging.info(f"Project type changed from {old_type} to {project_type}")
            
        session['current_project'] = project_name
        session['project_type'] = project_type
        session['available_outputs'] = OUTPUTS_FOR_PROJECT_TYPE[project_type]

        # Update tables and files when project changes
        if old_project != project_name:
            username = session.get('username', 'default')
            projects_dir = os.path.join('users', username, 'projects')
            project_dir = os.path.join(projects_dir, project_name)
            
            # Update tables
            tables = []
            structures_dir = os.path.join(project_dir, 'data', 'structures')
            if os.path.exists(structures_dir):
                tables = [f.replace('_structure.json', '') for f in os.listdir(structures_dir)
                        if f.endswith('_structure.json')]
            session['available_tables'] = tables
            
            # Update uploaded files
            uploaded_files = []
            uploads_dir = os.path.join(project_dir, 'uploads')
            if os.path.exists(uploads_dir):
                uploaded_files = [f for f in os.listdir(uploads_dir)
                                if os.path.isfile(os.path.join(uploads_dir, f))]
            session['uploaded_files'] = uploaded_files
            
            # Update context instance
            context = ContextManager.get_instance()
            context.available_tables = tables
            context.uploaded_files = uploaded_files
    
    @staticmethod
    def list_projects_tables_and_files(username):
        try:
            # Get projects
            projects = list_projects()
            
            # Get structure files for current project
            tables = []
            uploaded_files = []
            if session.get('current_project'):
                # Get tables from S3
                structures_path = get_project_structures_path()
                if structures_path:
                    # Get all files in structures directory
                    structure_files = list_files_in_s3(structures_path)
                    # Extract table names from structure files
                    tables = [os.path.basename(f).replace('_structure.json', '') 
                             for f in structure_files 
                             if f.endswith('_structure.json')]
                    
                # Get uploaded files from S3
                uploads_path = get_project_uploads_path()
                if uploads_path:
                    uploaded_files = [os.path.basename(f) 
                                    for f in list_files_in_s3(uploads_path)]
            
            # Log changes
            old_tables = session.get('available_tables', [])
            if set(old_tables) != set(tables):
                logging.info(f"Available tables changed from {old_tables} to {tables}")
            
            # Update session and context
            session['available_tables'] = tables
            context = ContextManager.get_instance()
            context.available_tables = tables
            
            return projects, tables, uploaded_files, OUTPUTS_FOR_PROJECT_TYPE[session['project_type']]
            
        except Exception as e:
            logging.error(f"Error listing projects, tables and files: {str(e)}")
            return [], [], []

# Instead of creating the instance directly, provide a function to get it
def get_user_context():
    return ContextManager.get_instance()