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
    "financial": {
        "revenueTable": "recipes",
        "ingredientsTable": "ingredients",
        "capexTable": "CAPEX",
        "opexTable": "OPEX",
        "employeesTable": "employees",
        "comparablesTable": "comparables",
        "historicalIS": "hist_IS"
    },
    "catalyst": {
        "fundamentalsTable": "fundamentals",
        "investmentTeamTable": "investment_team",
        "feesKeyTermsTable": "fees_key_terms",
        "seedTermsTable": "seed_terms",
        "serviceProvidersTable": "service_providers",
        "dealHistoryTable": "deal_history"
    }
}



EXPLANATION_FILES_DIR = os.path.join(os.getcwd(), "static", "json_explanations")
RUNNING_SUMMARY_DIR = os.path.join(os.getcwd(), "temp_business_data")
PROMPT_DIR = os.path.join(os.getcwd(), "static", "prompts")


RUNNING_SUMMARY_FILE = os.path.join(RUNNING_SUMMARY_DIR,'running_summary.txt')
