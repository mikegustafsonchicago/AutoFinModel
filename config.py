# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 21:54:45 2024

@author: mikeg
"""

import os

MAX_TOKENS_PER_CALL = 14984
OPENAI_MODEL = 'gpt-4o'

# Folder where your PDF files are located
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist


#Maps the inbound table name with the name of the json file to reference
TABLE_MAPPING = {
    "capexTable": "CAPEX",
    "opexTable": "OPEX",
    "employeesTable": "employees",
    "comparablesTable": "comparables",
    "financialsTable": "financials",
    "ingredientsTable": "ingredients",
    "revenueTable": "recipes"
}


EXPLANATION_FILES_DIR = os.path.join(os.getcwd(), "static", "json_explanations")
RUNNING_SUMMARY_DIR = os.path.join(os.getcwd(), "temp_business_data")
PROMPT_DIR = os.path.join(os.getcwd(), "static")
PROMPT_FILE = os.path.join(PROMPT_DIR, "prompt.txt")

# Explanation file paths for each table
TABLE_EXPLANATIONS = {
    "revenueTable": os.path.join(EXPLANATION_FILES_DIR, "revenueTable_explanation.txt"),
    "capexTable": os.path.join(EXPLANATION_FILES_DIR, "capex_explanation.txt"),
    "opexTable": os.path.join(EXPLANATION_FILES_DIR, "opex_explanation.txt"),
    "employeesTable": os.path.join(EXPLANATION_FILES_DIR, "employeesTable_explanation.txt"),
    "comparablesTable": os.path.join(EXPLANATION_FILES_DIR, "comparablesTable_explanation.txt"),
    "financialsTable": os.path.join(EXPLANATION_FILES_DIR, "financialsTable_explanation.txt"),
    "ingredientsTable": os.path.join(EXPLANATION_FILES_DIR, "ingredientsTable_explanation.txt"),
}

RUNNING_SUMMARY_FILE = os.path.join(RUNNING_SUMMARY_DIR,'running_summary.txt')
