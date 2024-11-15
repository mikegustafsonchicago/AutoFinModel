# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 09:27:46 2024

@author: mikeg
"""

import os
import json
import logging
from datetime import datetime
from config import TABLE_MAPPING, EXPLANATION_FILES_DIR


# Configure logging
logging.basicConfig(level=logging.DEBUG,  # Set level to DEBUG for maximum output
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # Ensure output goes to the console

# Folder where the JSON files will be stored
JSON_FOLDER = os.path.join(os.getcwd(), 'temp_business_data')

# JSON file names and corresponding placeholder structures
FILES_AND_STRUCTURES = {
    "CAPEX.json": {
        "expenses": [
            {
                "expense_name": "Placeholder",
                "amount": 0,
                "purchase_year": 2024,
                "depreciation_life": 5,
                "source_link": "",
                "source_string": "Placeholder",
                "notes": "This is a placeholder item"
            }
        ]
    },
    "comparables.json": {
        "Enterprise Value": {
            "value": 0,
            "notes": "Placeholder enterprise value."
        },
        "Market Cap": {
            "value": 0,
            "notes": "Placeholder market cap."
        },
        "EBITDA": {
            "value": 0,
            "notes": "Placeholder EBITDA."
        },
        "Equity Beta": {
            "value": 0,
            "notes": "Placeholder equity beta."
        },
        "Asset Beta": {
            "value": 0,
            "notes": "Placeholder asset beta."
        },
        "EV/EBITDA": {
            "value": 0,
            "notes": "Placeholder EV/EBITDA."
        }
    },
    "employees.json": {
        "employees": [
            {
                "role": "Placeholder Role",
                "number": 0,
                "wage": 0,
                "wage_type": "salary",
                "monthly_hours": 0,
                "notes": "This is a placeholder item",
                "source_link": "",
                "source_string": "Placeholder"
            }
        ]
    },
    "financials.json": {
        "1995": {
            "Revenue": None,
            "Direct Costs": None,
            "SG&A": None,
            "Employee Salaries": None,
            "EBITDA": None,
            "Depreciation": None,
            "EBIT": None,
            "Interest": None,
            "Taxes": None,
            "Net Income": None
        }
    },
    "ingredients.json": {
        "purchases_table": [
            {
                "ingredient_id": 1,
                "ingredient_name": "Ingredient A",
                "price_data_raw": [
                    {
                        "unit_name": "Standard Box",
                        "price": 5.0,
                        "selling_quantity": "10",
                        "unit": "box",
                        "company": "Example Inc.",
                        "source": "example.com"
                    },
                    {
                        "unit_name": "Bulk Pack",
                        "price": 4.5,
                        "selling_quantity": "20",
                        "unit": "box",
                        "company": "Bulk Supplies Co.",
                        "source": "bulksupplies.com"
                    }
                ]
            },
            {
                "ingredient_id": 2,
                "ingredient_name": "Ingredient B",
                "price_data_raw": [
                    {
                        "unit_name": "Single Pack",
                        "price": 3.0,
                        "selling_quantity": "1",
                        "unit": "package",
                        "company": "Packaged Goods Ltd.",
                        "source": "packagedgoods.com"
                    },
                    {
                        "unit_name": "Family Pack",
                        "price": 10.0,
                        "selling_quantity": "5",
                        "unit": "package",
                        "company": "Family Value Inc.",
                        "source": "familyvalue.com"
                    }
                ]
            }
        ]
    },
    "OPEX.json": {
        "expenses": [
            {
                "expense_name": "Placeholder",
                "amount": 0,
                "frequency": "",
                "source_link": "",
                "source_string": "Placeholder",
                "notes": "This is a placeholder item"
            }
        ]
    },
    "recipes.json":   { 'recipes':
        [
           {
              "name": "Recipe 1",
              "price": 50,
              "price_notes": "Sample price note",
              "ingredients": [
                 {
                    "amount": 2,
                    "ingredient_id": 1,
                    "ingredient_name": "Ingredient A",
                    "notes": "Sample ingredient note",
                    "price": 10,
                    "unit": "kg"
                 },
                 {
                    "amount": 1,
                    "ingredient_id": 2,
                    "ingredient_name": "Ingredient B",
                    "notes": "Sample ingredient note",
                    "price": 8,
                    "unit": "g"
                 }
              ]
           },
           {
              "name": "Recipe 2",
              "price": 30,
              "price_notes": "Another price note",
              "ingredients": [
                 {
                    "amount": 1,
                    "ingredient_id": 2,
                    "ingredient_name": "Ingredient B",
                    "notes": "Sample ingredient note",
                    "price": 8,
                    "unit": "g"
                 }
              ]
           }
        ]
    }

}
    
# Define placeholder structures for the Catalyst project
# Define placeholder structures for the Catalyst project
CATALYST_FILES_AND_STRUCTURES = {
    "fundamentals.json": [
        {
        "firm_name": "Placeholder Firm",
        "founded_year": 2020,
        "primary_office": "Placeholder City",
        "ownership_structure": "Placeholder Structure",
        "total_employees": 0,
        "diversity_status": "Placeholder Status",
        "website": "www.placeholder.com",
        "source_string": "Placeholder Source",
        "source_link": "https://example.com"
        }
    ],
    "investment_team.json":[
        {
            "investment_team_member_name": "Placeholder Name",
            "investment_team_member_title": "Placeholder Title",
            "investment_team_member_join_date": 2020,
            "source_string": "Placeholder Source",
            "source_link": "https://example.com"
        },
        {
            "investment_team_member_name": "Another Name",
            "investment_team_member_title": "Another Title",
            "investment_team_member_join_date": 2023,
            "source_string": "Another Source",
            "source_link": "https://example.com"
        }
    ],
    "fees_key_terms.json": [
        {
        "currency": "USD",
        "target_fundraise": "$0 million",
        "management_fee": "0%",
        "carried_interest": "0%",
        "preferred_return": "0%",
        "investment_period": "0 years",
        "fund_term": "0 years",
        "GP_commitment": "0%",
        "GP_commitment_funding_source": "Placeholder Source",
        "source_string": "Placeholder Source",
        "source_link": "https://example.com"
    }
    ],
    "seed_terms.json": [
        {
            "expense_name": "Target Seed Investment Placeholder",  # Placeholder for Target Seed Investment
            "initial_investment": "Initial Seed Investment Placeholder",  # Placeholder for Initial Seed Investment
            "fundraising_date": "Placeholder Date",  # Placeholder for Seed Fundraising Timeline
            "revenue_share": "0%",  # Placeholder for Revenue Share
            "revenue_share_cap": "0.0x",  # Placeholder for Revenue Share Cap
            "revenue_share_tail": "0%",  # Placeholder for Revenue Share Tail
            "source_string": "Placeholder Source",
            "source_link": "https://example.com"
        }
    ]
}



# Function to initialize JSON files with placeholders for a new project
def initialize_json_files(project_name):
    logging.debug(f"Project name is {project_name}")
    if project_name == "catalyst":
        files_and_structures = CATALYST_FILES_AND_STRUCTURES
    else:
        files_and_structures = FILES_AND_STRUCTURES  # Default to financial model placeholders
    
    for table_name, default_content in files_and_structures.items():
        file_path = os.path.join(JSON_FOLDER, table_name)
        if os.path.exists(JSON_FOLDER):
            with open(file_path, 'w') as json_file:
                json.dump(default_content, json_file, indent=4)
        else:
            logging.info(f"Error: File path for {table_name} not found. \n attempted {file_path}")



# Function to load JSON data for a given table
def load_table_json(table_identifier, project_name="financial"):
    """
    Load JSON data for a given table based on the project name.
    :param table_identifier: The identifier of the table to load data for.
    :param project_name: The project name to determine which JSON structure to load (default is "financial").
    :return: The loaded JSON data.
    """
    json_folder = os.path.join(os.getcwd(), 'temp_business_data')  # Path to JSON files

    # Determine file paths based on the project name and table identifier
    if project_name == "catalyst":
        # Catalyst-specific file paths with corrected identifiers
        file_mapping = {
            "fundamentals": "fundamentals.json",
            "investmentTeam": "investment_team.json",  # Updated to match "investmentTeam"
            "feesKeyTerms": "fees_key_terms.json",      # Updated to match "feesKeyTerms"
            "seedTerms": "seed_terms.json"              # Updated to match "seedTerms"
        }
    else:
        # Financial model-specific file paths (default)
        file_mapping = {
            "revenue": "recipes.json",
            "purchases": "ingredients.json",
            "CAPEX": "CAPEX.json",
            "OPEX": "OPEX.json",
            "employees": "employees.json",
            "comparables": "comparables.json",
            "financials": "financials.json"
        }

    # Get the file name based on table identifier
    file_name = file_mapping.get(table_identifier)
    if not file_name:
        logging.error(f"No JSON file mapped for table identifier: {table_identifier}")
        return None

    # Construct the file path
    file_path = os.path.join(json_folder, file_name)

    # Load the JSON data from the file
    try:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        logging.error(f"JSON file not found at path: {file_path}")
        return None

    
    
def load_json_explanation(table_name):
    """
    Load the explanation text for the given table name using EXPLANATION_FILES_DIR.
    The file name is constructed as "<table_name>_explanation.txt".
    """
    # Construct the file path for the explanation file
    explanation_file = os.path.join(EXPLANATION_FILES_DIR, f"{table_name}_explanation.txt")
    
    try:
        with open(explanation_file, 'r') as file:
            explanation_text = file.read()
            return explanation_text
    except FileNotFoundError:
        logging.error(f"Explanation file for {table_name} not found at {explanation_file}")
        return "No explanation available."
    except Exception as e:
        logging.error(f"Error reading explanation file for {table_name}: {e}")
        return "No explanation available."

    
def update_json_files(json_data, project_name):
    """
    Updates JSON files with new data for each table, restricted to the active project.
    :param json_data: A dictionary where keys are table names and values are data to update.
    :param project_name: The active project name (e.g., "financial" or "catalyst").
    """
    # Get the correct mapping based on the project name
    if project_name not in TABLE_MAPPING:
        logging.error(f"Invalid project name: {project_name}")
        return
    
    file_mapping = TABLE_MAPPING[project_name]
    
    for table_name, new_data in json_data.items():
        file_name = file_mapping.get(table_name)
        if not file_name:
            logging.warning(f"No mapping found for table: {table_name} in project {project_name}")
            continue

        # Ensure the file has a .json extension
        if not file_name.endswith(".json"):
            file_name += ".json"

        file_path = os.path.join(JSON_FOLDER, file_name)

        # Replace existing data entirely with new data
        try:
            with open(file_path, "w") as json_file:
                json.dump(new_data, json_file, indent=4)  # Write new_data directly
            logging.info(f"Successfully updated {file_name} for project {project_name}")
        except Exception as e:
            logging.error(f"Failed to update {file_name} for project {project_name}: {e}")




# Function to fix incomplete JSON by adding missing closing brackets
def fix_incomplete_json(json_string):
    open_curly = json_string.count('{')
    close_curly = json_string.count('}')
    open_square = json_string.count('[')
    close_square = json_string.count(']')

    # Add missing curly braces if necessary
    if open_curly > close_curly:
        json_string += '}' * (open_curly - close_curly)
    # Add missing square brackets if necessary
    if open_square > close_square:
        json_string += ']' * (open_square - close_square)

    return json_string



# Function to save the parsed JSON data to a file
def save_json_to_file(json_data):
    # Create a folder to store JSON files if it doesn't exist
    save_directory = os.path.join(os.getcwd(), 'temp_business_data')
    os.makedirs(save_directory, exist_ok=True)

    # Create a timestamped file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"openai_response_{timestamp}.json"
    file_path = os.path.join(save_directory, file_name)

    # Save the JSON data to the file
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    logging.info(f"Saved JSON response to {file_path}")