import logging
import os
import io
import sys
from dotenv import load_dotenv
import json
from datetime import datetime as dt
from datetime import timedelta
from flask import Flask, request, jsonify, render_template, send_file, g, session
from flask_session import Session
import boto3
import uuid
# Internal module imports
from user_management import *
import api_processing
from excel_generation.auto_financial_modeling import generate_excel_model
from json_manager import JsonManager
from file_manager import *
from session_info_manager import SessionInfoManager
from prompt_builder import PromptBuilder
from excel_generation.catalyst_partners_page import make_catalyst_summary
from powerpoint_generation.ppt_financial import generate_ppt
from powerpoint_generation.ppt_fund_analysis import generate_fund_analysis_ppt
from powerpoint_generation.ppt_real_estate import generate_real_estate_ppt
from config import (  
    DEVELOPMENT_ENVIRONMENT,
    ALLOWABLE_PROJECT_TYPES, 
    OUTPUTS_FOR_PROJECT_TYPE,
    LOCAL_PORT,
    HOSTED_PORT
)
from context_manager import initialize_session_context, get_application_context, get_or_create_user_id, initialize_empty_project_context, load_project_context
from middleware import inject_context





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
    
    # Initialize user management
    user_management = UserManagement(app)
    app.config['user_management'] = user_management

    # Initialize core services
    app.config['json_manager'] = JsonManager()
    app.config['prompt_manager'] = PromptBuilder(app.config['json_manager'])
    app.config['session_info_manager'] = SessionInfoManager()

    Session(app)  # Initialize the extension

    logging.debug("[create_app] Services initialized")

    return app

app = create_app()

#=============================================================
# SESSION MANAGEMENT
#=============================================================
@app.before_request
def before_request():
    """Ensure user session before each request"""
    app.config['user_management'].ensure_user_session()


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
    return render_template('index.html', title="Application")



@app.route('/api/init')
def get_init_data():
    """Get initialization data for the frontend application."""
    logging.info("\n\n----Starting /api/init endpoint----")
    try:
        init_data = initialize_session_context()
        logging.debug(f"[get_init_data] Username: {session['user']['username']}")
        return jsonify(init_data), 200

    except Exception as e:
        logging.error(f"Error in init: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500



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
    username = session['user']['username']  # From before_request
    current_project = session['current_project']['name']  # From before_request
    project_type = session['current_project']['type']  # From before_request
    
    try:
        json_manager = app.config['json_manager']
        schema = json_manager.get_table_schema(table_name)
        
        if schema and schema.get("structure"):
            return jsonify(schema)
        else:
            return jsonify({"error": f"No schema defined for {table_name}"}), 404
            
    except Exception as e:
        logging.error(f"[get_table_schema] Error retrieving schema for '{table_name}': {str(e)}", exc_info=True)
        logging.error(f"[get_table_schema] Current context - User: {username}, Project: {current_project}")
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
    username = session['user']['username']  # From before_request
    current_project = session['current_project']['name']  # From before_request
    project_type = session['current_project']['type']  # From before_request
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
    username = session['user']['username']  # From before_request
    current_project = session['current_project']['name']  # From before_request
    project_type = session['current_project']['type']  # From before_request
    logging.info("\n\n----Clear Data----\n\n")
    logging.debug(f"Call to clear all data. Missing an init and clear call that were in context_manager.py")

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
    username = session['user']['username']  # From before_request
    current_project = session['current_project']['name']  # From before_request
    project_type = session['current_project']['type']  # From before_request

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
                s3_path = f"users/{username}/projects/{current_project}/uploads/{uploaded_file.filename}"
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
        username = session['user']['username']  # From before_request
        current_project = session['current_project']['name']  # From before_request
        metadata_path = f"users/{username}/projects/{current_project}/project_metadata.json"
        
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
                "project_owner": username,
                "file_count": 0,
                "last_output_generated": None,
                "collaborators": [username],
                "visibility": "private",
                "access_level": {
                    username: "admin"
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
def get_context():
    """Get context including user, projects, and uploaded files."""
    try:
        context_data = get_application_context()
        context_str = (
            f"\n[/api/context] Retrieved context data:\n"
            f"----------------------------------------\n"
            f"User: {context_data.get('user', {}).get('username')}\n"
            f"Current Project: {context_data.get('current_project', {}).get('name')}\n" 
            f"Project Type: {context_data.get('current_project', {}).get('type')}\n"
            f"Available Tables: {context_data.get('current_project', {}).get('available_tables')}\n"
            f"Uploaded Files: {context_data.get('current_project', {}).get('uploaded_files')}\n"
            f"----------------------------------------\n"
        )
        #logging.debug(context_str)
        return jsonify(context_data), 200

    except Exception as e:
        logging.error(f"Error getting context data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500



@app.route('/api/gallery')
@inject_context
def get_gallery_images():
    username = session['user']['username']  # From before_request
    current_project = session['current_project']['name']  # From before_request
    try:
        # Get gallery contents
        image_files = get_gallery_contents()
        
        if image_files is None:
            return jsonify([])
            
        # Create list of image objects with proxied URLs
        images = []
        for filename in image_files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Use a proxied URL instead of direct S3 URL
                proxied_url = f"/api/image/{username}/{current_project}/gallery/{filename}"
                images.append({
                    'name': filename,
                    'url': proxied_url
                })
            else:
                logging.debug(f"Skipping non-image file: {filename}")
        
        return jsonify(images)
        
    except Exception as e:
        logging.error(f"Error getting gallery images: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Add new endpoint to proxy images
@app.route('/api/image/<username>/<project>/gallery/<filename>')
def get_image(username, project, filename):
    username = session['user']['username']  # From before_request
    current_project = session['current_project']['name']  # From before_request
    try:
        s3_path = f"users/{username}/projects/{current_project}/gallery/{filename}"
        
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
def create_project():
    logging.debug("\n\n\n----Create Project----")
    try:
        data = request.json
        project_name = data.get('projectName')
        project_type = data.get('projectType')
        
        initialize_empty_project_context(project_name, project_type) # Initialize the project context in session
        create_new_project(project_name) # Create the folder structure in S3    
        initialize_session_files(app.config['json_manager']) # Copy the JSON structure files from static to S3
        
        return jsonify({"message": "Project created successfully"}), 200

    except Exception as e:
        logging.error(f"[create_project] Error creating project: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/projects/load', methods=['POST'])
@inject_context
def load_project():
    try:
        data = request.json
        project_name = data.get('projectName')
        
        if not project_name:
            return jsonify({"error": "Project name is required"}), 400

        project_context = load_project_context(project_name)
        return jsonify({
            "message": "Project loaded successfully",
            "projectName": project_context['name'],
            "projectType": project_context['type'],
            "metadata": project_context['metadata']
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
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

        username = session.get('user')['username']
        current_project = session.get('current_project')['name']
        
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
                    available_projects = session['user']['portfolio']['projects']
                    
                    if item_name not in available_projects:
                        errors.append(f"Project does not exist: {item_name}")
                        continue

                    # Delete the project directory and contents
                    delete_result = delete_project(item_name)
                    
                    if not delete_result:
                        errors.append(f"Failed to delete project: {item_name}")
                        continue

                    # If deleting current project, clear project context
                    if current_project == item_name:
                        session.pop('current_project', None)
                        session.pop('project_type', None)

                    results.append(f"Project {item_name} deleted successfully")

                elif delete_type in ['file', 'gallery']:
                    # Project name required for file/gallery operations
                    if not project_name:
                        errors.append(f"Project name is required for {delete_type} deletion: {item_name}")
                        continue

                    # Construct S3 path based on type
                    if delete_type == 'file':
                        s3_path = f"users/{username}/projects/{current_project}/uploads/{item_name}"
                    else:  # gallery
                        s3_path = f"users/{username}/projects/{current_project}/gallery/{item_name}"

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
    logging.info("\n\n\n-----Download Output Endpoint-----")
    try:
        username = session.get('user')['username']
        current_project = session.get('current_project')
        output_type = request.args.get('type')
        project_type = current_project.get('type')
        
        if not output_type:
            logging.error(f"[/download_output] No output type found for user: {username}")
            return jsonify({"error": "Output type is required"}), 400
            
        if not project_type:
            logging.error(f"[/download_output] No project type found for user: {username}")
            return jsonify({"error": "Project type is required"}), 400

        if project_type not in ALLOWABLE_PROJECT_TYPES.values():
            logging.error(f"[/download_output] Invalid project type: {project_type}")
            return jsonify({"error": "Invalid project type"}), 400

        # Validate output type is allowed for this project type
        if output_type not in OUTPUTS_FOR_PROJECT_TYPE.get(project_type, []):
            logging.error(f"[/download_output] Output type {output_type} not allowed for project type {project_type}. Allowed types for {project_type}: {OUTPUTS_FOR_PROJECT_TYPE.get(project_type, [])}. User: {username}, Project: {current_project.get('name')}")
            return jsonify({"error": f"Output type {output_type} not available for {project_type} projects"}), 400

        # Get the outputs directory for this user's project
        outputs_path = get_project_outputs_path()
        
        if not outputs_path:
            logging.error("[/download_output] Failed to get project outputs path")
            return jsonify({"error": "Could not access project outputs directory"}), 500

        # Generate the appropriate file based on output type and get the S3 path
        logging.info(f"[/download_output] Starting file generation for output type: {output_type}")
        if output_type in ['excel_model', 'excel_overview']:
            if project_type == "financial":
                logging.debug("[/download_output] Generating financial Excel model")
                file_path = generate_excel_model()
            elif project_type == "catalyst":
                logging.debug("[/download_output] Generating catalyst Excel summary")
                file_path = make_catalyst_summary()
            else:
                logging.error(f"[/download_output] Excel output not supported for project type: {project_type}")
                return jsonify({"error": "Excel output not supported for this project type"}), 400
        elif output_type == 'powerpoint_overview':
            if project_type == "financial":
                file_path = generate_ppt()
            elif project_type == "real_estate":
                from powerpoint_generation.ppt_real_estate import generate_ppt
                file_name = generate_real_estate_ppt()
                file_path = f"{outputs_path}/{file_name}"
            elif project_type == "fund_analysis":
                logging.info("[/download_output] Generating fund analysis PowerPoint")
                from powerpoint_generation.ppt_fund_analysis import generate_fund_analysis_ppt
                
                # Generate PowerPoint and get the file object/bytes
                ppt_bytes = generate_fund_analysis_ppt(debug=debug)
                
                # Generate a unique filename
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"fund_analysis_{timestamp}.pptx"
                s3_path = f"{outputs_path}/{filename}"
                
                # Upload bytes directly to S3
                try:
                    s3_client.put_object(
                        Bucket=BUCKET_NAME,
                        Key=s3_path,
                        Body=ppt_bytes
                    )
                    file_path = s3_path
                    logging.info(f"[/download_output] Successfully uploaded PowerPoint to S3: {s3_path}")
                except Exception as e:
                    logging.error(f"[/download_output] Failed to upload PowerPoint to S3: {str(e)}")
                    return jsonify({"error": "Failed to save PowerPoint"}), 500
            else:
                logging.error(f"[/download_output] PowerPoint generation not supported for project type: {project_type}")
                return jsonify({"error": "PowerPoint generation not supported for this project type"}), 400
        else:
            logging.error(f"[/download_output] Invalid output type: {output_type}")
            return jsonify({"error": "Invalid output type"}), 400

        # Download from S3 to temporary file
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        temp_path = os.path.join(temp_dir, filename)
        
        if not download_file_from_s3(file_path, temp_path):
            logging.error(f"[/download_output] Failed to download file from S3: {file_path}")
            return jsonify({"error": f"Failed to retrieve {output_type} file"}), 500

        logging.info(f"[/download_output] Successfully retrieved {output_type} file from S3: {file_path}")

        try:
            response = send_file(temp_path, as_attachment=True)
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"
            
            # Instead of deleting immediately, schedule the file for deletion after the response
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception as e:
                    logging.error(f"[/download_output] Failed to clean up temporary file: {e}")
            
            return response
            
        except Exception as e:
            logging.error(f"[/download_output] Error preparing file for download: {str(e)}")
            # Clean up if send_file fails
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({"error": "Failed to prepare file for download"}), 500

    except Exception as e:
        logging.error(f"[/download_output] Error generating {output_type} file: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to generate {output_type} file: {str(e)}"}), 500


#=============================================================
# MAIN ENTRY POINT
#=============================================================
if __name__ == '__main__':
    
    load_dotenv()
    
    # Use local port for development, hosted port for production
    if DEVELOPMENT_ENVIRONMENT == "DEBUG":
        port = int(LOCAL_PORT)
        debug = True
    else:
        port = int(HOSTED_PORT)
        debug = False
    
    app.run(host='0.0.0.0', port=port, debug=debug)


@app.route('/api/user/set_secret_key', methods=['POST'])
def set_secret_key():
    """Set or update the user's secret key"""
    try:
        data = request.get_json()
        secret_key = data.get('secret_key')
        
        if not secret_key:
            return jsonify({'error': 'No secret key provided'}), 400
            
        if app.config['user_management'].set_user_secret_key(secret_key):
            return jsonify({'message': 'Secret key updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update secret key'}), 400
            
    except Exception as e:
        logging.error(f"Error setting secret key: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
