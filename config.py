# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 21:54:45 2024

@author: mikeg
"""

import os

MAX_TOKENS_PER_CALL = 14984
OPENAI_MODEL = 'gpt-4o-mini'
OPENAI_COST_PER_INPUT_TOKEN = 2.5/1000000
OPENAI_COST_PER_OUTPUT_TOKEN = 10/1000000

DEFAULT_project_type = "financials"

# Top-level folder for the data
USER_DATA_FOLDER = os.path.join(os.getcwd(), 'users')
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist

SESSION_LOG_FOLDER = os.path.join(os.getcwd(), 'session_logs')

ALLOWED_EXTENSIONS = {'.pdf', '.txt'}
ALLOWED_GALLERY_EXTENSIONS = {'.pdf', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.ico', '.webp'}

RUNNING_SUMMARY_DIR = os.path.join(os.getcwd(), "temp_business_data")
BASE_PROMPT_DIR = os.path.join(os.getcwd(), "static", "prompts")
STRUCTURE_FILES_DIR = os.path.join(os.getcwd(), "static", "json_structure_data")

BUCKET_NAME = 'autofinmodel'

# Dictionary mapping table names to their structure files for financial project
FINANCIALS_TABLE = [
    "capital_expenses_structure.json",
    "comparable_companies_structure.json",
    "cost_of_sales_structure.json",
    "employees_structure.json", 
    "historical_financials_structure.json",
    "operating_expenses_structure.json",
    "revenue_structure.json"
]

CATALYST_TABLE = [
    "deal_history_structure.json",
    "fees_key_terms_structure.json",
    "fundamentals_structure.json", 
    "investment_team_structure.json",
    "seed_terms_structure.json",
    "service_providers_structure.json"
]

REAL_ESTATE_TABLE = [
    "property_zoning_structure.json",
    "property_financials_structure.json",
    "property_fundamentals_structure.json"
]

TA_GRADING_TABLE = [
    "GRADING_business_description_structure.json",
    "GRADING_SUCCESS_structure.json",
    "GRADING_MMMM_structure.json",
    "GRADING_FACES_structure.json"
]

ALLOWABLE_PROJECT_TYPES = {"Financial Model": "financial", "Catalyst": "catalyst", "Real Estate": "real_estate", "TA Grading": "ta_grading"}

RUNNING_SUMMARY_FILE = os.path.join(RUNNING_SUMMARY_DIR,'running_summary.txt')


OUTPUTS_FOR_PROJECT_TYPE = {
    "financial": ["excel_model", "powerpoint_overview"],
    "catalyst": ["excel_overview"],
    "real_estate": ["powerpoint_overview"],
    "ta_grading": []
}

# Default metadata schema for new projects
DEFAULT_PROJECT_METADATA = {
    # Basic Info
    "project_type": None,  # Set dynamically
    "created_at": None,  # Set at creation time
    "last_modified_at": None,  # Set at creation time
    
    # Project Details
    "project_description": "",  # To be updated by user
    "project_tags": [],  # To be updated by user
    "project_owner": None,  # Set to username at creation
    
    # Technical Details
    "file_count": 0,  # Updated when files added/removed
    "last_output_generated": None,  # Updated when outputs generated
    
    # Access Control
    "collaborators": [],  # Initially set to owner only
    "visibility": "private",  # Default to private
    "access_level": {}  # Owner gets admin access
}
