from flask import Flask, request, jsonify, render_template, send_file, session
import logging
import os
import api_processing
from excel_generation.auto_financial_modeling import generate_excel_model
from json_manager import load_table_json
from file_manager import initialize_session_files
from datetime import datetime, timedelta
from config import UPLOAD_FOLDER

from prompt_builder import PromptBuilder
from catalyst_partners_page import make_catalyst_summary



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
prompt_manager = None



# Serve the frontend HTML (if needed)
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/app')
def application():
    project_name = "financial"
    initialize_session_files(project_name)
    return render_template('index.html', title="Application")

@app.route('/catalyst')
def catalyst():
    project_name = "catalyst"
    return render_template('catalyst.html', title="Catalyst")

@app.route('/set_data')
def set_data():
    # Mark session as "permanent" so it doesn’t expire when the browser is closed
    session.permanent = True
    
    # Set session-specific data
    session['user_uploads'] = []
    
    return 'Session data has been set for this user.'


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
        prompt_manager=prompt_manager
    )
    logging.info("\n\n***************END OPENAI API CALL*************************\n\n\n")
    logging.debug(f" Response data is {response_data}")
    # Send back only the text. JSON gets read from the data files.
    return jsonify({
        "text": response_data.get("text", "")
    }), status_code


# Route to serve table data (CAPEX, OPEX, etc.)
@app.route('/api/table_data/<project_name>/<table_identifier>', methods=['GET'])
def get_table_data(project_name, table_identifier):
    table_data = load_table_json(table_identifier, project_name)
    return jsonify(table_data)
   

@app.route('/download_excel', methods=['GET'])
def download_excel():
    project_name = request.args.get('project_name')
    if not project_name:
        return jsonify({"error": "Project name is required to generate the Excel file"}), 400
    elif project_name == "financial":
        download_name = "financial_model.xlsx"
    elif project_name == "catalyst":
        download_name = 'Catalyst_Partners_Summary.xlsx'

    # Generate Excel file based on the project_name
    if project_name == "financial":
        file_path = generate_excel_model()  # Pass project_name to your Excel generation function
    elif project_name == "catalyst":
        file_path = make_catalyst_summary()

    # Serve the file to the frontend
    return send_file(file_path, as_attachment=True, download_name=download_name)


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
    initialize_session_files(project_name)

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
        prompt_manager = PromptBuilder(project_name)
    return prompt_manager

if __name__ == '__main__':
    app.run(debug=True)