# context_manager.py
from dataclasses import dataclass
from flask import session
from typing import Optional
import logging
import os


@dataclass
class UserContext:
    username: str
    current_project: Optional[str] = None
    project_type: Optional[str] = None
    available_projects: list[str] = None
    available_tables: list[str] = None

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
        
        return cls._instance

    @staticmethod
    def initialize_session(username):
        logging.debug(f"[ContextManager.initialize_session] Initializing session for user: {username}")
        old_username = session.get('username')
        if old_username != username:
            logging.info(f"Username changed from {old_username} to {username}")
        session['username'] = username
        
        old_projects = session.get('available_projects', [])
        if old_projects != []:
            logging.info(f"Available projects reset from {old_projects} to []")
        session['available_projects'] = []
        session['available_tables'] = []

    @staticmethod
    def set_project_context(project_name, project_type):
        logging.debug(f"[ContextManager.set_project_context] Setting project context: name: {project_name}, type: {project_type}")
        old_project = session.get('current_project')
        old_type = session.get('project_type')
        
        if old_project != project_name:
            logging.info(f"Current project changed from {old_project} to {project_name}")
        if old_type != project_type:
            logging.info(f"Project type changed from {old_type} to {project_type}")
            
        session['current_project'] = project_name
        session['project_type'] = project_type
    

    @staticmethod
    def list_projects_and_tables(username):
        """
        List all project names and structure files for the current user and update context.
        
        Args:
            username (str): The username to get projects and tables for
            
        Returns:
            tuple: (list of project names, list of table names) or (empty list, empty list) if none found
        """
        try:
            # Get projects
            projects_dir = os.path.join('users', username, 'projects')
            projects = []
            if os.path.exists(projects_dir):
                projects = [d for d in os.listdir(projects_dir) 
                        if os.path.isdir(os.path.join(projects_dir, d))]
                
            # Get structure files for current project
            tables = []
            if session.get('current_project'):
                structures_dir = os.path.join(projects_dir, session['current_project'], 'data', 'structures')
                if os.path.exists(structures_dir):
                    tables = [f.replace('_structure.json', '') for f in os.listdir(structures_dir)
                            if f.endswith('_structure.json')]
            
            # Log changes
            old_projects = session.get('available_projects', [])
            old_tables = session.get('available_tables', [])
            
            if set(old_projects) != set(projects):
                logging.info(f"Available projects changed from {old_projects} to {projects}")
            if set(old_tables) != set(tables):
                logging.info(f"Available tables changed from {old_tables} to {tables}")
            
            # Update session and context instance
            session['available_projects'] = projects
            session['available_tables'] = tables
            
            context = ContextManager.get_instance()
            context.available_projects = projects
            context.available_tables = tables
            
            return projects, tables
            
        except Exception as e:
            logging.error(f"Error listing projects and tables for user {username}: {str(e)}")
            return [], []

# Instead of creating the instance directly, provide a function to get it
def get_user_context():
    return ContextManager.get_instance()