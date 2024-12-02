# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 21:54:45 2024

@author: mikeg
"""

import os

MAX_TOKENS_PER_CALL = 14984
OPENAI_MODEL = 'gpt-4o'
OPENAI_COST_PER_INPUT_TOKEN = 2.5/1000000
OPENAI_COST_PER_OUTPUT_TOKEN = 10/1000000

DEFAULT_PROJECT_NAME = "financials"

# Folder where your PDF files are located
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist

JSON_FOLDER = os.path.join(os.getcwd(), 'temp_business_data')


STRUCTURE_FILES_DIR = os.path.join(os.getcwd(), "static", "json_structure_data")
RUNNING_SUMMARY_DIR = os.path.join(os.getcwd(), "temp_business_data")
PROMPT_DIR = os.path.join(os.getcwd(), "static", "prompts")

# Dictionary mapping table names to their structure files for financial project
FINANCIALS_TABLE = {
    "capital_expenditures": "capital_expenses_structure.json",
    "comparables": "comparable_companies_structure.json",
    "cost_of_sales": "cost_of_sales_structure.json", 
    "employees": "employees_structure.json",
    "historical_financials": "historical_financials_structure.json",
    "operating_expenses": "operating_expenses_structure.json",
    "revenue": "revenue_structure.json"
}

CATALYST_TABLE = {
    "deal_history": "deal_history_structure.json",
    "fees_key_terms": "fees_key_terms_structure.json",
    "fundamentals": "fundamentals_structure.json",
    "investment_team": "investment_team_structure.json",
    "seed_terms": "seed_terms_structure.json",
    "service_providers": "service_providers_structure.json"
}


RUNNING_SUMMARY_FILE = os.path.join(RUNNING_SUMMARY_DIR,'running_summary.txt')