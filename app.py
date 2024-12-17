import logging
import os
import sys
import json
from datetime import timedelta
from flask import Flask, request, jsonify, render_template, send_file, session, g

# Internal module imports
import api_processing
from excel_generation.auto_financial_modeling import generate_excel_model
from json_manager import JsonManager
from file_manager import (
    initialize_session_files,
    create_new_user,
    get_project_structures_path,
    get_project_uploads_path,
    create_new_project,
    list_users,
    list_projects
)
from session_info_manager import SessionInfoManager
from prompt_builder import PromptBuilder
from excel_generation.catalyst_partners_page import make_catalyst_summary
from powerpoint_generation.ppt_financial import generate_ppt
from config import ALLOWED_EXTENSIONS
from context_manager import ContextManager
from middleware import inject_context

#=============================================================
# LOGGING CONFIGURATION
#=============================================================
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Ensure logs go to console
)


#=============================================================
# APPLICATION FACTORY
#=============================================================
def create_app():
    """Create and configure the Flask application."""
    logging.debug("[create_app] Starting application initialization...")

    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    app.secret_key = 'your_secret_key'
    app.permanent_session_lifetime = timedelta(days=1)

    logging.debug("[create_app] Flask app created with basic configuration")

    # Initialize core services and store them in app config
    app.config['json_manager'] = JsonManager()
    app.config['prompt_manager'] = PromptBuilder(app.config['json_manager'])
    app.config['session_info_manager'] = SessionInfoManager()

    logging.debug("[create_app] Services initialized: JsonManager, PromptBuilder, SessionInfoManager")

    @app.before_request
    def ensure_user_session():
        """Ensure that a user session is established before each request."""
        if 'username' not in session:
            # Setup a default user and project context if none exists
            ContextManager.initialize_session('test_user')
            ContextManager.set_project_context('test_project', 'financial')
            logging.debug("[before_request] Initialized default session for test_user")

    return app

app = create_app()


#=============================================================
# ROUTES: FRONTEND VIEWS
#=============================================================
@app.route('/')
def landing():
    """Serve a landing page."""
    return render_template('landing.html')


@app.route('/app')
@inject_context
def application():
    """Main application page."""
    logging.info("\n\n\n----Refresh----")
    context = ContextManager.get_instance()
    return render_template('index.html', title="Application")


@app.route('/catalyst')
@inject_context
def catalyst():
    """Catalyst page."""
    logging.info("\n\n\n----Refresh----")
    context = ContextManager.get_instance()

    if not os.path.exists(os.path.join(os.getcwd(), 'temp_business_data')):
        initialize_session_files(app.config['json_manager'])

    # PromptManager initialized if needed
    prompt_manager = app.config['prompt_manager']

    return render_template('catalyst.html', title="Catalyst")


@app.route('/real_estate')
@inject_context
def real_estate():
    """Real Estate page."""
    logging.info("\n\n\n----Refresh----")
    context = ContextManager.get_instance()

    if not os.path.exists(os.path.join(os.getcwd(), 'temp_business_data')):
        initialize_session_files(app.config['json_manager'])

    prompt_manager = app.config['prompt_manager']

    return render_template('real_estate.html', title="Real Estate")


@app.route('/api/init')
@inject_context
def get_init_data():
    """Get initialization data for the frontend application."""
    context = ContextManager.get_instance()
    
    try:
        # Get current user's projects
        projects = list_projects()
        
        # Check if current project exists in projects list
        current_project = context.current_project if context.current_project in projects else None
        
        # If no current project, set to first available if any
        if current_project is None and projects:
            logging.warning("Current project mismatch; setting to first available project.")
            current_project = projects[0]
            ContextManager.set_project_context(current_project, context.project_type)
        
        init_data = {
            'user': {
                'username': context.username,
                'isAuthenticated': 'username' in session
            },
            'project': {
                'currentProject': current_project,
                'projectType': context.project_type,
                'availableProjects': projects
            },
            'system': {
                'hasExistingFiles': os.path.exists(os.path.join(os.getcwd(), 'temp_business_data')),
                'isInitialized': bool(app.config.get('json_manager'))
            }
        }
        
        logging.debug(f"Initialization data prepared: {init_data}")
        return jsonify(init_data), 200
        
    except Exception as e:
        logging.error(f"Error getting initialization data: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/set_data')
@inject_context
def set_data():
    """
    Example route to demonstrate setting session data.
    """
    session.permanent = True
    session['user_uploads'] = []
    return 'Session data has been set for this user.'


#=============================================================
# ROUTES: API ENDPOINTS
#=============================================================

@app.route('/api/schema/<table_name>')
@inject_context
def get_table_schema(table_name):
    """
    Get the schema (structure) of a given table.
    The schema defines the columns and their properties.
    """
    try:
        json_manager = app.config['json_manager']
        schema = json_manager.get_table_schema(table_name)
        
        if schema:
            return jsonify(schema)
        else:
            return jsonify({"error": f"No schema defined for {table_name}"}), 404
            
    except Exception as e:
        logging.error(f"Error retrieving schema for {table_name}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error retrieving schema for {table_name}: {str(e)}"}), 500


@app.route('/api/openai', methods=['POST'])
def call_openai():
    logging.info("\n\n\n----OpenAI Call----")
    """Handle requests to the OpenAI API."""
    data = request.json
    prompt_manager = app.config['prompt_manager']

    response_data, status_code = api_processing.manage_api_calls(
        business_description=data.get('businessDescription'),
        user_input=data.get('userPrompt'),
        update_scope=data.get('updateScope'),
        file_name=data.get('fileName'),
        prompt_manager=prompt_manager,
        json_manager=app.config['json_manager']
    )

    return jsonify({"text": response_data.get("text", "")}), status_code


@app.route('/api/table_data/<table_identifier>', methods=['GET'])
def get_table_data(table_identifier):
    """
    Load and return JSON data for a given table identifier.
    This data should match the schema retrieved from /api/schema/<table_name>.
    """
    context = ContextManager.get_instance()
    try:
        json_manager = app.config['json_manager']
        table_data = json_manager.load_json_data(table_identifier)
        if table_data is None:
            return jsonify({"error": f"No data found for table {table_identifier}"}), 404
        return jsonify({"data": table_data})
    except Exception as e:
        logging.error(f"Error loading data for table {table_identifier}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error loading data for table {table_identifier}: {str(e)}"}), 500


@app.route('/api/clear_data', methods=['POST'])
@inject_context
def clear_all_data():
    """
    Clear all data (reinitialize session files and reset prompts).
    """
    context = ContextManager.get_instance()
    logging.info("\n\n----Clear Data----\n\n")
    ContextManager.initialize_session(context.username)
    ContextManager.set_project_context(context.current_project, context.project_type)

    initialize_session_files(app.config['json_manager'])
    prompt_manager = app.config['prompt_manager']
    prompt_manager.reset_prompts()

    return jsonify({"message": "All data cleared successfully!"}), 200


@app.route('/api/upload_file', methods=['POST'])
@inject_context
def upload_file():
    """
    Upload a file to the server.
    """
    context = ContextManager.get_instance()
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_ext = os.path.splitext(uploaded_file.filename)[1].lower()

    if uploaded_file and file_ext in ALLOWED_EXTENSIONS:
        uploads_dir = get_project_uploads_path()
        save_path = os.path.join(uploads_dir, uploaded_file.filename)
        uploaded_file.save(save_path)
        return jsonify({
            "message": f"File {uploaded_file.filename} uploaded successfully!",
            "file_path": save_path
        }), 200
    else:
        allowed_ext_list = ', '.join(ALLOWED_EXTENSIONS)
        return jsonify({"error": f"Only the following file types are allowed: {allowed_ext_list}"}), 400


@app.route('/api/context')
@inject_context
def get_context():
    """
    Get context including user, projects, and uploaded files.
    """
    try:
        context = ContextManager.get_instance()
        
        # Get user's projects
        projects = list_projects()
        
        # Get uploads directory contents
        uploads_path = get_project_uploads_path()
        uploaded_files = []
        if uploads_path and os.path.exists(uploads_path):
            uploaded_files = [f for f in os.listdir(uploads_path) 
                              if os.path.isfile(os.path.join(uploads_path, f))]
                              
        # Get structure files
        structures_path = get_project_structures_path()
        available_tables = []
        if structures_path and os.path.exists(structures_path):
            available_tables = [f for f in os.listdir(structures_path)
                              if os.path.isfile(os.path.join(structures_path, f))]
        context_data = {
            "username": context.username,
            "current_project": context.current_project,
            "project_type": context.project_type,
            "available_projects": projects,
            "uploaded_files": uploaded_files,
            "available_tables": available_tables
        }
        
        return jsonify(context_data), 200
        
    except Exception as e:
        logging.error(f"Error getting context data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


#=============================================================
# ROUTES: PROJECT MANAGEMENT
#=============================================================
@app.route('/api/projects/new', methods=['POST'])
@inject_context
def create_project_route():
    """
    Create a new project directory structure and initialize its files.
    """
    logging.info("\n\n\n\n-----Create Project-----")
    try:
        context = ContextManager.get_instance()
        data = request.json
        project_name = data.get('projectName')
        project_type = data.get('projectType')
        logging.debug(f"Creating project {project_name} of type {project_type} for user {context.username}")

        if not project_name or not project_type:
            return jsonify({"error": "Project name and type are required"}), 400

        if not create_new_project(project_name):
            return jsonify({"error": "Failed to create project directories"}), 500

        ContextManager.set_project_context(project_name, project_type)
        context = ContextManager.get_instance()

        initialize_session_files(app.config['json_manager'])

        return jsonify({"message": "Project created successfully"})
    except Exception as e:
        logging.error(f"Error creating project: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/projects/load', methods=['POST'])
@inject_context
def load_project():
    """
    Load an existing project into the current session context.
    """
    try:
        context = ContextManager.get_instance()
        data = request.json
        project_name = data.get('projectName')
        project_type = data.get('projectType')
        logging.debug(f"Loading project {project_name} of type {project_type} for user {context.username}")

        if not project_name:
            return jsonify({"error": "Project name is required"}), 400

        # Validate project existence
        available_projects = list_projects()
        if project_name not in available_projects:
            return jsonify({"error": "Project does not exist"}), 404

        ContextManager.set_project_context(project_name, project_type)

        return jsonify({"message": "Project loaded successfully"})
    except Exception as e:
        logging.error(f"Error loading project: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


#=============================================================
# ROUTES: FILE DOWNLOADS (EXCEL / PPT)
#=============================================================
@app.route('/download_excel', methods=['GET'])
@inject_context
def download_excel():
    """
    Generate and download the Excel model file for the current project.
    """
    try:
        context = g.context
        logging.debug(f"Attempting to generate Excel file for project: {context.project_type}")

        if not context.project_type:
            return jsonify({"error": "Project type is required to generate the Excel file"}), 400

        if context.project_type not in ["financial", "catalyst"]:
            return jsonify({"error": "Invalid project type"}), 400

        file_path = generate_excel_model() if context.project_type == "financial" else make_catalyst_summary()

        if not os.path.exists(file_path):
            logging.error(f"Generated Excel file not found at path: {file_path}")
            return jsonify({"error": "Failed to generate Excel file"}), 500

        logging.info(f"Successfully generated Excel file at: {file_path}")
        filename = os.path.basename(file_path)

        response = send_file(file_path, as_attachment=True)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response
    except Exception as e:
        logging.error(f"Error generating Excel file: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to generate Excel file: {str(e)}"}), 500


@app.route('/download_ppt', methods=['GET'])
@inject_context
def download_ppt():
    """
    Generate and download the PowerPoint file for the current project.
    """
    try:
        context = g.context
        logging.debug(f"Attempting to generate PowerPoint file for project: {context.project_type}")

        if not context.project_type:
            return jsonify({"error": "Project type is required to generate the PowerPoint file"}), 400

        if context.project_type not in ["financial", "catalyst", "real_estate"]:
            return jsonify({"error": "Invalid project type"}), 400

        current_dir = os.path.dirname(os.path.abspath(__file__))
        ppt_dir = os.path.join(current_dir, 'powerpoint_generation')
        output_path = os.path.join(ppt_dir, 'output_ppt.pptx')

        logging.info(f"Generating PowerPoint file for {context.project_type} project")
        sys.path.append(ppt_dir)
        generate_ppt()

        if not os.path.exists(output_path):
            logging.error(f"Generated PowerPoint file not found at path: {output_path}")
            return jsonify({"error": "Failed to generate PowerPoint file"}), 500

        logging.info(f"Successfully generated PowerPoint file at: {output_path}")
        filename = os.path.basename(output_path)

        response = send_file(output_path, as_attachment=True)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response
    except Exception as e:
        logging.error(f"Error generating PowerPoint file: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to generate PowerPoint file: {str(e)}"}), 500


#=============================================================
# MAIN ENTRY POINT
#=============================================================
if __name__ == '__main__':
    app.run(debug=True)
