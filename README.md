# Financial and Catalyst Modeling Software

## Overview
This project automates the process of generating financial and private equity summaries using AI. It processes uploaded PDFs, extracts key data, and integrates it into structured JSON files and detailed Excel reports. The software supports two primary projects:
1. **Financial Modeling**: Traditional financial models for businesses, including CAPEX, OPEX, and revenue projections.
2. **Catalyst Partners**: Summarizes private equity firm data, including investment team, firm fundamentals, and fees.

## Table of Contents
1. [Overview](#overview)
2. [Setup](#setup)
3. [Features](#features)
4. [Modules](#modules)
   - [app.py](#app-py)
   - [api_processing.py](#api-processing-py)
   - [prompt_builder.py](#prompt-builder-py)
   - [json_manager.py](#json-manager-py)
   - [catalyst_partners_page.py](#catalyst-partners-page-py)
5. [Usage](#usage)
6. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites
- Python 3.11
- Flask
- XlsxWriter
- Tabulator.js
- Anaconda (optional, for managing Python environments)

### Installation
1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd [project-directory]
Install dependencies:
bash
Copy code
pip install -r requirements.txt
Create the following directories if they do not exist:
temp_business_data/
uploads/
static/json_explanations/
Update config.py to reflect your environment setup, including:
UPLOAD_FOLDER
EXPLANATION_FILES_DIR
RUNNING_SUMMARY_DIR
Start the application:
bash
Copy code
python app.py
Access the application via localhost:5000.
Features
Multi-Project Support:
Handles projects dynamically using the project_type parameter (financial or catalyst).
Each project uses a specific prompt and JSON structure.
Dynamic JSON Management:
JSON files are initialized, updated, and validated dynamically for each project.
Files include placeholders or are populated with OpenAI responses.
Excel Generation:
Generates Excel files with tailored formatting for financial and catalyst models.
Uses a YAML configuration for flexible styles.
PDF Text Extraction:
Extracts content page by page for token-efficient processing.
Dynamically chunks content based on token limits.
OpenAI Integration:
Prompts and responses are dynamically managed via PromptBuilder.
Handles running summaries and table-specific data explanations.
Modules
app.py
Purpose: The main Flask application handling API routes for:
/api/upload_pdf: Upload PDFs.
/api/openai: Process PDFs and generate JSON data.
/download_excel: Download the generated Excel file.
Key Updates: Supports project_type to differentiate between financial and catalyst projects.
api_processing.py
Purpose: Manages OpenAI API calls, including payload preparation, token management, and JSON updates.
Key Features:
manage_api_calls: Dynamically manages the API workflow based on the project.
prepare_payload: Constructs the API request, integrating project-specific JSON files.
Dependency: Requires PromptBuilder and json_manager.py.
prompt_builder.py
Purpose: Builds system and user prompts dynamically based on the project.
Key Features:
Adds table data dynamically to prompts.
Generates project-specific system and user prompts.
Supports both financial and catalyst use cases with respective explanation files.
json_manager.py
Purpose: Manages JSON data for all projects, including initialization, loading, and validation.
Key Features:
initialize_json_files: Creates placeholder files for the project.
update_json_files: Updates JSON data dynamically with API responses.
Mapping: Uses FILES_AND_STRUCTURES (financial) and CATALYST_FILES_AND_STRUCTURES (catalyst) to ensure accurate file handling.
catalyst_partners_page.py
Purpose: Handles Excel generation for Catalyst Partners summaries.
Key Features:
Dynamically writes data such as investment team, fees, and fundamentals into a formatted Excel sheet.
Uses the write_to_sheet method to apply formatting and manage rows.
Usage
Running the Application
To start the Flask server:

bash
Copy code
python app.py
Access the application at http://localhost:5000.

Project Selection
The project_type parameter (financial or catalyst) determines which templates, JSON files, and prompts are used:

financial: Business financial model with CAPEX, OPEX, and other tables.
catalyst: Private equity evaluation focusing on team, fees, and terms.
Key Endpoints
/api/openai: Processes PDF data based on the active project and updates JSON files.
/api/clear_data: Clears all project-specific JSON files.
/download_excel: Generates and downloads the formatted Excel file.
Troubleshooting
ValueError: prompt_manager must be initialized:

Ensure project_type is passed correctly in API calls.
Verify that the PromptBuilder is initialized for the project.
DuplicateWorksheetName:

Ensure unique sheet names are used for each Excel generation process.
AttributeError: 'str' object has no attribute '_get_xf_index':

Ensure that the correct format names are passed in YAML configurations.
Logs:

Enable debug logs by setting LOGGING_LEVEL = logging.DEBUG in config.py.
Directory Structure
bash
Copy code
/website
├── app.py                 # Main application script
├── api_processing.py      # OpenAI API management
├── catalyst_partners_page.py # Catalyst-specific Excel generation
├── json_manager.py        # JSON data handling
├── static/
│   ├── js/                # JavaScript for table handling
│   ├── json_explanations/ # Table explanation files
│   └── prompts/           # Prompt templates
├── templates/             # HTML templates
├── uploads/               # Uploaded PDFs
├── temp_business_data/    # JSON files for financial and catalyst projects
├── excel_generation/      # All Excel generation logic
