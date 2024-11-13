# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 09:27:46 2024

@author: mikeg
"""

import os
import json
import logging
from datetime import datetime
from config import TABLE_MAPPING, TABLE_EXPLANATIONS


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

# Function to initialize JSON files with placeholders for a new project
def initialize_json_files():
    # Only overwrite if explicitly required
    for table_name, default_content in FILES_AND_STRUCTURES.items():
        file_path = os.path.join(JSON_FOLDER, table_name)
        if os.path.exists(file_path):
            with open(file_path, 'w') as json_file:
                json.dump(default_content, json_file, indent=4)
        else:
            logging.info(f"Error: File path for {table_name} not found. \n attempted {file_path}")



# Function to load JSON data for a given table
def load_table_json(table_identifier):
    json_folder = os.path.join(os.getcwd(), 'temp_business_data')  # Path to your JSON files
    if table_identifier == "revenue":
        file_path = os.path.join(json_folder, 'recipes.json')
    elif table_identifier == "purchases":
        file_path = os.path.join(json_folder, 'ingredients.json')
    elif table_identifier == "CAPEX":
        file_path = os.path.join(json_folder, 'CAPEX.json')
    elif table_identifier == "OPEX":
        file_path = os.path.join(json_folder, 'OPEX.json')
    elif table_identifier == "employees":
        file_path = os.path.join(json_folder, 'employees.json')

    # Load the JSON file
    with open(file_path, 'r') as json_file:
        return json.load(json_file)
    
    
def load_json_explanation(table_name):
    """
    Load the explanation text for the given table name.
    """
    explanation_file = TABLE_EXPLANATIONS.get(table_name)
    if explanation_file:
        try:
            with open(explanation_file, 'r') as file:
                explanation_text = file.read()
                return explanation_text
        except FileNotFoundError:
            logging.error(f"Explanation file for {table_name} not found at {explanation_file}")
            return "No explanation available."
    else:
        logging.warning(f"No explanation path configured for {table_name}")
        return "No explanation available."

    
def update_json_files(json_data):
    """
    Updates JSON files with new data for each table.
    :param json_data: A dictionary where keys are table names and values are data to update.
    """
    for table_name, new_data in json_data.items():
        file_name = TABLE_MAPPING.get(table_name)
        if not file_name:
            logging.error(f"No mapping found for table: {table_name}")
            continue

        # Ensure the file has a .json extension
        if not file_name.endswith(".json"):
            file_name += ".json"

        file_path = os.path.join(JSON_FOLDER, file_name)
        
        # Replace existing data entirely with new data
        with open(file_path, "w") as json_file:
            json.dump(new_data, json_file, indent=4)  # Write new_data directly
        logging.info(f"Successfully updated {file_name}")



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