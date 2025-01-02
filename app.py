import logging
import os
import sys
import json
from datetime import timedelta
from flask import Flask, request, jsonify, render_template, send_file, g, session
from flask_session import Session
import boto3
# Internal module imports
import api_processing
from excel_generation.auto_financial_modeling import generate_excel_model
from json_manager import JsonManager
from file_manager import *
from session_info_manager import SessionInfoManager
from prompt_builder import PromptBuilder
from excel_generation.catalyst_partners_page import make_catalyst_summary
from powerpoint_generation.ppt_financial import generate_ppt
from config import (
    ALLOWED_EXTENSIONS, 
    ALLOWED_GALLERY_EXTENSIONS, 
    ALLOWABLE_PROJECT_TYPES, 
    OUTPUTS_FOR_PROJECT_TYPE
)
from context_manager import ContextManager
from middleware import inject_context
import uuid
from datetime import datetime
import io

#=============================================================
# LOGGING CONFIGURATION
#=============================================================
# Reduce boto3/s3transfer logging
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('s3transfer').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Configure your app's logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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

     # Configure server-side sessions
    app.config['SESSION_TYPE'] = 'filesystem'  
    app.config['SESSION_FILE_DIR'] = './flask_session_data'  # Example path
    app.config['SESSION_PERMANENT'] = False

    Session(app)  # Initialize the extension

    logging.debug("[create_app] Services initialized: JsonManager, PromptBuilder, SessionInfoManager")

    @app.before_request
    def ensure_user_session():
        """Ensure that a user session is established before each request."""
        if 'username' not in session:
            # Generate a unique user ID combining timestamp and UUID
            unique_id = f"user_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
            
            # Setup a unique user context
            ContextManager.initialize_session(unique_id)
            ContextManager.set_project_context('new_project', 'financial')
            
            # Store in session
            session['username'] = unique_id
            session.permanent = True  # Make the session persistent

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



@app.route('/api/init')
@inject_context
def get_init_data():
    """Get initialization data for the frontend application."""
    logging.info("\n\n----Starting /api/init endpoint----")
    
    context = ContextManager.get_instance()
    logging.debug(f"Got context instance with username: {context.username}")
    
    try:
        projects = list_projects()
        current_project = context.current_project if context.current_project in projects else None
        
        # Get metadata for current project if one exists
        project_metadata = None
        if current_project:
            project_metadata = get_project_metadata()
        
        init_data = {
            'user': {
                'username': context.username,
                'isAuthenticated': 'username' in session
            },
            'project': {
                'currentProject': current_project,
                'projectType': context.project_type,
                'availableProjects': projects,
                'metadata': project_metadata  # Add metadata here
            },
            'system': {
                'hasExistingFiles': bool(get_project_data_contents()),
                'isInitialized': bool(app.config.get('json_manager'))
            }
        }
        
        return jsonify(init_data), 200
        
    except Exception as e:
        logging.error(f"Error in init: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


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
    Get the schema (structure) and display settings of a given table.
    The schema defines the columns and their properties.
    """
    context = ContextManager.get_instance()
    logging.debug(f"[get_table_schema] Retrieving schema for table '{table_name}' in project '{context.current_project}' of type '{context.project_type}'")
    try:
        json_manager = app.config['json_manager']
        logging.debug(f"[get_table_schema] Retrieved json_manager instance {id(json_manager)} from app config")
        
        schema = json_manager.get_table_schema(table_name)
        logging.debug(f"[get_table_schema] Schema lookup completed. Found schema: {schema is not None}")
        if schema and schema.get("structure"):
            logging.debug(f"[get_table_schema] Schema contains structure and display settings")
            return jsonify(schema)
        else:
            logging.debug(f"[get_table_schema] No schema found for table '{table_name}' in project structures")
            return jsonify({"error": f"No schema defined for {table_name}"}), 404
            
    except Exception as e:
        logging.error(f"[get_table_schema] Error retrieving schema for '{table_name}': {str(e)}", exc_info=True)
        logging.error(f"[get_table_schema] Current context - User: {context.username}, Project: {context.current_project}")
        return jsonify({"error": f"Error retrieving schema for {table_name}: {str(e)}"}), 500


@app.route('/api/openai', methods=['POST'])
def call_openai():
    logging.info("\n\n\n----OpenAI Call----")
    """Handle requests to the OpenAI API."""
    data = request.json
    logging.debug(f"[call_openai] Received data: {data}")
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
    Upload a file to Amazon S3 using file_manager.py's upload functionality.
    Handles both regular files (ALLOWED_EXTENSIONS) and gallery images (ALLOWED_GALLERY_EXTENSIONS).
    """
    context = ContextManager.get_instance()

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    uploaded_file = request.files['file']
    destination = request.form.get('destination', 'uploads')  # Default to uploads if not specified
    
    if uploaded_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save file temporarily
        temp_path = os.path.join('temp', uploaded_file.filename)
        os.makedirs('temp', exist_ok=True)
        uploaded_file.save(temp_path)

        try:
            if destination == 'gallery':
                success = upload_to_s3_gallery(temp_path, "main", uploaded_file.filename)
            else:  # uploads
                s3_path = f"users/{context.username}/projects/{context.current_project}/uploads/{uploaded_file.filename}"
                success = upload_file_to_s3(temp_path, s3_path)

            if success:
                return jsonify({
                    "message": f"File {uploaded_file.filename} uploaded successfully!",
                    "destination": destination
                }), 200
            else:
                return jsonify({"error": "Failed to upload file"}), 500

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logging.error(f"Error handling file upload: {str(e)}")
        return jsonify({"error": f"Failed to process file upload: {str(e)}"}), 500


def ensure_project_metadata(project_name):
    """
    Ensure that a project has metadata, creating it if it doesn't exist.
    """
    try:
        context = ContextManager.get_instance()
        metadata_path = f"users/{context.username}/projects/{project_name}/project_metadata.json"
        
        # Try to read existing metadata
        metadata = read_json(metadata_path)
        
        if not metadata:
            # Create default metadata for legacy project
            metadata = {
                "project_type": "real_estate",  # Default type
                "created_at": datetime.now().isoformat(),  # Use current time as creation time
                "last_modified_at": datetime.now().isoformat(),
                "project_description": "",
                "project_tags": [],
                "project_owner": context.username,
                "file_count": 0,
                "last_output_generated": None,
                "collaborators": [context.username],
                "visibility": "private",
                "access_level": {
                    context.username: "admin"
                }
            }
            
            # Write the new metadata
            write_json(metadata_path, metadata)
            logging.info(f"Created metadata for legacy project: {project_name}")
            
        return metadata
    except Exception as e:
        logging.error(f"Error ensuring metadata for project {project_name}: {str(e)}")
        return None

@app.route('/api/context')
@inject_context
def get_context():
    """Get context including user, projects, and uploaded files."""
    try:
        context = ContextManager.get_instance()
        projects = list_projects()
        
        # Get metadata for current project
        project_metadata = get_project_metadata() if context.current_project else None
        
        # Get available structure files instead of data tables
        available_tables = get_available_structure_files() or []
        
        context_data = {
            "username": context.username,
            "current_project": context.current_project,
            "project_type": context.project_type,
            "available_projects": projects,
            "uploaded_files": get_uploads_contents(),
            "available_tables": available_tables,  # Now using structure files
            "project_types": list(ALLOWABLE_PROJECT_TYPES.keys()),
            "available_outputs": context.available_outputs,
            "project_metadata": project_metadata,
            "project_info": {
                "created_at": project_metadata.get("created_at") if project_metadata else None,
                "last_modified_at": project_metadata.get("last_modified_at") if project_metadata else None,
                "file_count": project_metadata.get("file_count", 0) if project_metadata else 0
            }
        }
        
        logging.debug(f"Context data prepared. Available tables: {available_tables}")
        return jsonify(context_data), 200
        
    except Exception as e:
        logging.error(f"Error getting context data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
@app.route('/api/gallery')
@inject_context
def get_gallery_images():
    logging.info("\n\n\n----Gallery Images Request----")
    context = ContextManager.get_instance()
    try:
        project = request.args.get('project')
        project_type = request.args.get('type')
        
        logging.debug(f"Getting gallery images for project: {project}, type: {project_type}")
        
        # Get gallery contents
        image_files = get_gallery_contents()
        logging.debug(f"Retrieved {len(image_files) if image_files else 0} files from gallery")
        
        if image_files is None:
            logging.debug("No image files found in gallery")
            return jsonify([])
            
        # Create list of image objects with proxied URLs
        images = []
        for filename in image_files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Use a proxied URL instead of direct S3 URL
                proxied_url = f"/api/image/{context.username}/{project}/gallery/{filename}"
                images.append({
                    'name': filename,
                    'url': proxied_url
                })
                logging.debug(f"Added image to response: {filename}")
            else:
                logging.debug(f"Skipping non-image file: {filename}")
        
        logging.debug(f"Returning {len(images)} images")
        return jsonify(images)
        
    except Exception as e:
        logging.error(f"Error getting gallery images: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Add new endpoint to proxy images
@app.route('/api/image/<username>/<project>/gallery/<filename>')
def get_image(username, project, filename):
    try:
        s3_path = f"users/{username}/projects/{project}/gallery/{filename}"
        
        # Get image from S3
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_path)
        image_data = response['Body'].read()
        
        # Determine content type
        content_type = response['ContentType']
        
        return send_file(
            io.BytesIO(image_data),
            mimetype=content_type,
            as_attachment=False,
            download_name=filename
        )
    except Exception as e:
        logging.error(f"Error retrieving image: {str(e)}")
        return jsonify({"error": "Image not found"}), 404



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
    logging.debug(f"New Project | {request.json}")
    try:
        context = ContextManager.get_instance()
        data = request.json
        project_name = data.get('projectName')
        project_type = data.get('projectType')  # Now receiving project type name directly
        
        if not project_name or not project_type:
            return jsonify({"error": "Project name and type are required"}), 400

        # Get the internal project type value from ALLOWABLE_PROJECT_TYPES
        internal_project_type = ALLOWABLE_PROJECT_TYPES.get(project_type)
        if not internal_project_type:
            return jsonify({"error": f"Invalid project type: {project_type}"}), 400

        if not create_new_project(project_name):
            return jsonify({"error": "Failed to create project directories"}), 500

        ContextManager.set_project_context(project_name, internal_project_type)
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
    logging.info("\n\n\n-----Load Project-----")
    try:
        context = ContextManager.get_instance()
        data = request.json
        project_name = data.get('projectName')
        logging.debug(f"[load_project] Request data: {data}")
        
        if not project_name:
            logging.warning("[load_project] No project name provided in request")
            return jsonify({"error": "Project name is required"}), 400

        # Validate project existence
        available_projects = list_projects()
        logging.debug(f"[load_project] Available projects: {available_projects}")
        if project_name not in available_projects:
            logging.warning(f"[load_project] Project does not exist: {project_name}")
            return jsonify({"error": "Project does not exist"}), 404

        # Get metadata BEFORE changing context
        metadata = get_project_metadata()
        logging.debug(f"[load_project] Retrieved metadata: {metadata}")
        if not metadata:
            logging.error("[load_project] Failed to retrieve project metadata")

        project_type = metadata.get('project_type', 'real_estate')  # Default to real_estate if not specified
        logging.debug(f"[load_project] Project type: {project_type}")
        
        # Now set the context with both name and type together
        ContextManager.set_project_context(project_name, project_type)
        logging.info(f"[load_project] Successfully set context for project: {project_name}")

        return jsonify({
            "message": "Project loaded successfully",
            "projectName": project_name,
            "projectType": project_type,
            "metadata": metadata  # Send all metadata back to frontend
        })
    except Exception as e:
        logging.error(f"Error loading project: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/projects/delete', methods=['POST'])
@inject_context
def delete_project_endpoint():
    """
    Delete multiple projects, files, or gallery images based on the provided parameters.
    
    Expected request JSON format:
    {
        "items": [
            {
                "type": "project"|"file"|"gallery", # Required - type of item to delete
                "name": string,  # Required - name of item to delete
                "projectName": string  # Optional - required for file/gallery deletes
            },
            ...
        ]
    }
    """
    try:
        data = request.json
        items = data.get('items', [])

        if not items:
            return jsonify({"error": "No items provided for deletion"}), 400

        context = ContextManager.get_instance()
        results = []
        errors = []

        for item in items:
            delete_type = item.get('type')
            item_name = item.get('name')
            project_name = item.get('projectName')

            if not delete_type or not item_name:
                errors.append(f"Delete type and item name are required for item: {item}")
                continue

            try:
                if delete_type == 'project':
                    # Validate project existence
                    available_projects = list_projects()
                    
                    if item_name not in available_projects:
                        errors.append(f"Project does not exist: {item_name}")
                        continue

                    # Delete the project directory and contents
                    delete_result = delete_project(item_name)
                    
                    if not delete_result:
                        errors.append(f"Failed to delete project: {item_name}")
                        continue

                    # If deleting current project, clear project context
                    if context.current_project == item_name:
                        ContextManager.clear_project_context()

                    results.append(f"Project {item_name} deleted successfully")

                elif delete_type in ['file', 'gallery']:
                    # Project name required for file/gallery operations
                    if not project_name:
                        errors.append(f"Project name is required for {delete_type} deletion: {item_name}")
                        continue

                    # Construct S3 path based on type
                    if delete_type == 'file':
                        s3_path = f"users/{context.username}/projects/{project_name}/uploads/{item_name}"
                    else:  # gallery
                        s3_path = f"users/{context.username}/projects/{project_name}/gallery/{item_name}"

                    # Delete from S3
                    delete_result = delete_file_from_s3(s3_path)
                    
                    if not delete_result:
                        errors.append(f"Failed to delete {delete_type}: {item_name}")
                        continue

                    results.append(f"{delete_type.capitalize()} {item_name} deleted successfully")

                else:
                    errors.append(f"Invalid delete type for item: {item}")

            except Exception as item_error:
                errors.append(f"Error processing {delete_type} {item_name}: {str(item_error)}")

        response = {
            "message": "Deletion operation completed",
            "successes": results
        }
        if errors:
            response["errors"] = errors
            return jsonify(response), 207  # Multi-Status response

        return jsonify(response), 200


    except Exception as e:
        logging.error(f"delete_project_endpoint: Error in delete operation: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


#=============================================================
# ROUTES: FILE DOWNLOADS (EXCEL / PPT)
#=============================================================
@app.route('/download_output', methods=['GET'])
@inject_context
def download_output():
    """
    Generate and download the requested output file (Excel or PowerPoint) for the current project.
    """
    try:
        context = ContextManager.get_instance()
        output_type = request.args.get('type')
        
        if not output_type:
            logging.error(f"No output type found for user: {context.username}")
            return jsonify({"error": "Output type is required"}), 400
            
        if not context.project_type:
            logging.error(f"No project type found for user: {context.username}")
            return jsonify({"error": "Project type is required"}), 400

        if context.project_type not in ALLOWABLE_PROJECT_TYPES.values():
            logging.error(f"Invalid project type: {context.project_type}")
            return jsonify({"error": "Invalid project type"}), 400

        # Validate output type is allowed for this project type
        if output_type not in OUTPUTS_FOR_PROJECT_TYPE.get(context.project_type, []):
            return jsonify({"error": f"Output type {output_type} not available for {context.project_type} projects"}), 400

        logging.debug(f"Generating {output_type} for project type: {context.project_type}")

        # Get the outputs directory for this user's project
        outputs_path = get_project_outputs_path()
        if not outputs_path:
            return jsonify({"error": "Could not access project outputs directory"}), 500

        # Generate the appropriate file based on output type and get the S3 path
        if output_type in ['excel_model', 'excel_overview']:
            if context.project_type == "financial":
                file_path = generate_excel_model()
            elif context.project_type == "catalyst":
                file_path = make_catalyst_summary()
            else:
                return jsonify({"error": "Excel output not supported for this project type"}), 400
        elif output_type == 'powerpoint_overview':
            if context.project_type == "financial":
                file_path = generate_ppt()
            elif context.project_type == "real_estate":
                from powerpoint_generation.ppt_real_estate import generate_ppt
                file_name = generate_ppt()
                file_path = f"{outputs_path}/{file_name}"
            else:
                return jsonify({"error": "PowerPoint generation not supported for this project type"}), 400
        else:
            return jsonify({"error": "Invalid output type"}), 400

        # Download from S3 to temporary file
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        temp_path = os.path.join(temp_dir, filename)
        
        if not download_file_from_s3(file_path, temp_path):
            logging.error(f"Failed to download file from S3: {file_path}")
            return jsonify({"error": f"Failed to retrieve {output_type} file"}), 500

        logging.info(f"Successfully retrieved {output_type} file from S3: {file_path}")

        try:
            response = send_file(temp_path, as_attachment=True)
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"
            return response
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logging.error(f"Error generating {output_type} file: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to generate {output_type} file: {str(e)}"}), 500


def get_or_create_user_id():
    """Get existing user ID or create a new one."""
    if 'username' in session:
        return session['username']
    
    # Generate new unique ID
    unique_id = f"user_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
    session['username'] = unique_id
    session.permanent = True
    
    return unique_id


def get_available_tables():
    """Get list of available table structure files for the current project."""
    try:
        context = ContextManager.get_instance()
        tables_path = f"users/{context.username}/projects/{context.current_project}/data/structures"
        
        # List files in the structures directory
        tables = get_available_project_data_tables()
        logging.info(f"Found tables in {tables_path}: {tables}")  # Add this log
        
        # Filter for structure files
        structure_files = [t for t in tables if t.endswith('_structure.json')]
        logging.info(f"Filtered structure files: {structure_files}")  # Add this log
        
        return structure_files
    except Exception as e:
        logging.error(f"Error getting available tables: {str(e)}")
        return []


#=============================================================
# MAIN ENTRY POINT
#=============================================================
if __name__ == '__main__':
    app.run(debug=True)
