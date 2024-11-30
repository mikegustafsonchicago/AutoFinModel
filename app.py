from flask import Flask, request, jsonify, render_template, send_file, session
import logging
import os
import sys
import api_processing
from excel_generation.auto_financial_modeling import generate_excel_model
from json_manager import JsonManager
from file_manager import initialize_session_files
from datetime import datetime, timedelta
from config import UPLOAD_FOLDER

from prompt_builder import PromptBuilder
from excel_generation.catalyst_partners_page import make_catalyst_summary

from powerpoint_generation.ppt_generation import generate_ppt

# Configure logging
logging.basicConfig(level=logging.DEBUG,  # Set level to DEBUG for maximum output
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # Ensure output goes to the console


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)  # Ensure Flask's own logger is also set to DEBUG
app.secret_key = 'your_secret_key'  # This is needed for session encryption
app.permanent_session_lifetime = timedelta(days=1)  # Set session lifetime as needed


current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format the current time
logging.debug(f"\n\n\n------Website Refresh at {current_time}---------\n-----------------------------------------------------\n")

# Initialize prompt_manager as a global variable, but defer assignment
global prompt_manager, json_manager  # Add json_manager to global declaration
prompt_manager = None
json_manager = JsonManager()



# Serve the frontend HTML (if needed)
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/app')
def application():
    project_name = "financial"
    # Only initialize files if they don't exist
    if not os.path.exists(os.path.join(os.getcwd(), 'temp_business_data')):
        initialize_session_files(project_name, json_manager)
    return render_template('index.html', title="Application")

@app.route('/catalyst')
def catalyst():
    project_name = "catalyst"
    # Only initialize files if they don't exist
    if not os.path.exists(os.path.join(os.getcwd(), 'temp_business_data')):
        initialize_session_files(project_name, json_manager)
    return render_template('catalyst.html', title="Catalyst")

@app.route('/set_data')
def set_data():
    # Mark session as "permanent" so it doesn’t expire when the browser is closed
    session.permanent = True
    
    # Set session-specific data
    session['user_uploads'] = []
    
    return 'Session data has been set for this user.'


@app.route('/api/schema/<table_name>')
def get_table_schema(table_name):
    try:
        if table_name in json_manager.FILES_AND_STRUCTURES:
            schema = json_manager.FILES_AND_STRUCTURES[table_name].get('structure')
            if schema:
                return jsonify(schema)
        return jsonify({"error": f"No schema defined for {table_name}"}), 404
    except Exception as e:
        return jsonify({"error": f"Error retrieving schema for {table_name}: {str(e)}"}), 500
    
    

@app.route('/api/openai', methods=['POST'])
def call_openai():
    # Get the request data from the frontend
    data = request.json
    project_name = data.get('projectName')
    prompt_manager = get_prompt_manager(project_name)
    user_prompt = data.get('userPrompt')
    business_description = data.get('businessDescription')
    update_scope = data.get('updateScope')
    logging.info("\n\n***************BEGIN OPENAI API CALL*************************")
    logging.info(f"UPDATE SCOPE IS {update_scope}\n")

    pdf_file_name = data.get('pdfFileName')
    pdf_file_name = os.path.join(UPLOAD_FOLDER, pdf_file_name)
    logging.debug(f"In app.py in call_openai, project_name is {project_name}")
    logging.debug(f"In app.py in call_openai, data is {data}")
    response_data, status_code = api_processing.manage_api_calls(
        business_description=business_description,
        project_name = project_name, 
        user_input=user_prompt,
        update_scope=update_scope,
        pdf_name=pdf_file_name,
        prompt_manager=prompt_manager,
        json_manager=json_manager
    )
    logging.info("\n\n***************END OPENAI API CALL*************************\n\n\n")
    # Send back only the text. JSON gets read from the data files.
    return jsonify({
        "text": response_data.get("text", "")
    }), status_code


# Route to serve table data (CAPEX, OPEX, etc.)
@app.route('/api/table_data/<project_name>/<table_identifier>', methods=['GET'])
def get_table_data(project_name, table_identifier):
    # Get the appropriate file structures based on project
    files_and_structures = json_manager.CATALYST_FILES_AND_STRUCTURES if project_name == "catalyst" else json_manager.FILES_AND_STRUCTURES
    
    # Get the root key from the file structure
    root_key = files_and_structures[table_identifier]["root_key"] if table_identifier in files_and_structures else None
    
    # Load the table data
    table_data = json_manager.load_json_data(table_identifier, project_name)
    
    # Return both the data and root key
    return jsonify({
        "data": table_data,
        "root_key": root_key
    })
   

@app.route('/download_excel', methods=['GET'])
def download_excel():
    try:
        project_name = request.args.get('project_name')
        logging.debug(f"Attempting to generate Excel file for project: {project_name}")
        
        if not project_name:
            logging.error("No project name provided in request")
            return jsonify({"error": "Project name is required to generate the Excel file"}), 400
            
        # Validate project name is one of the expected values
        if project_name not in ["financial", "catalyst"]:
            logging.error(f"Invalid project name received: {project_name}")
            return jsonify({"error": "Invalid project name"}), 400
            
        # Generate Excel file
        logging.info(f"Generating Excel file for {project_name} project")
        file_path = generate_excel_model() if project_name == "financial" else make_catalyst_summary()
        logging.debug(f"In app.py in download_excel, file_path is {file_path}")
        # Verify file exists before attempting to send
        if not os.path.exists(file_path):
            logging.error(f"Generated Excel file not found at path: {file_path}")
            return jsonify({"error": "Failed to generate Excel file"}), 500
            
        logging.info(f"Successfully generated Excel file at: {file_path}")
        
        # Get filename from path
        filename = os.path.basename(file_path)
        
        # Set Content-Disposition header with filename
        response = send_file(file_path, as_attachment=True)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response 
        
    except Exception as e:
        logging.error(f"Error generating Excel file: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to generate Excel file: {str(e)}"}), 500


@app.route('/download_ppt', methods=['GET'])
def download_ppt():
    try:
        project_name = request.args.get('project_name')
        logging.debug(f"Attempting to generate PowerPoint file for project: {project_name}")
        
        if not project_name:
            logging.error("No project name provided in request")
            return jsonify({"error": "Project name is required to generate the PowerPoint file"}), 400
            
        # Validate project name is one of the expected values
        if project_name not in ["financial", "catalyst"]:
            logging.error(f"Invalid project name received: {project_name}")
            return jsonify({"error": "Invalid project name"}), 400
            
        # Get current directory and construct output path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ppt_dir = os.path.join(current_dir, 'powerpoint_generation')
        output_path = os.path.join(ppt_dir, 'output_ppt.pptx')
        
        # Generate PowerPoint file
        logging.info(f"Generating PowerPoint file for {project_name} project")
        
        # Import and run PPT generation script
        sys.path.append(ppt_dir)
        generate_ppt()
        
        # Verify file exists before attempting to send
        if not os.path.exists(output_path):
            logging.error(f"Generated PowerPoint file not found at path: {output_path}")
            return jsonify({"error": "Failed to generate PowerPoint file"}), 500
            
        logging.info(f"Successfully generated PowerPoint file at: {output_path}")
        
        # Get filename from path
        filename = os.path.basename(output_path)
        
        # Set Content-Disposition header with filename
        response = send_file(output_path, as_attachment=True)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response
        
    except Exception as e:
        logging.error(f"Error generating PowerPoint file: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to generate PowerPoint file: {str(e)}"}), 500



# Route to clear and re-initialize the JSON files
@app.route('/api/clear_data', methods=['POST'])
def clear_all_data():
    data = request.json

    # Validate that projectName is present in the payload
    project_name = data.get('projectName')
    if not project_name:
        logging.error("Project name is missing in the request.")
        return jsonify({"error": "Project name is required to clear data."}), 400

    # Log the project name and clear data
    logging.debug(f"Project name is {project_name}")
    initialize_session_files(project_name, json_manager)

    return jsonify({"message": "All data cleared successfully!"}), 200


# Route to handle PDF uploads
@app.route('/api/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400
    pdf_file = request.files['pdf']

    if pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        # Save the file to the uploads folder
        save_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        pdf_file.save(save_path)
        return jsonify({"message": f"File {pdf_file.filename} uploaded successfully!", "file_path": save_path}), 200
    else:
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
def get_prompt_manager(project_name):
    global prompt_manager
    if prompt_manager is None or prompt_manager.project_name != project_name:
        logging.debug(f"Initializing prompt_manager for project_name: {project_name}")
        prompt_manager = PromptBuilder(project_name, json_manager)
    return prompt_manager

if __name__ == '__main__':
    app.run(debug=True)