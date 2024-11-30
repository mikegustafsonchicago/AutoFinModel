# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 09:27:46 2024

@author: mikeg
"""
import sys
import os
import json
import logging
from datetime import datetime

from config import EXPLANATION_FILES_DIR
from excel_generation.ingredients_code import Ingredient

class JsonManager:
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.DEBUG,
                          format='%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                          handlers=[logging.StreamHandler()])

        # Folder where JSON files are stored
        self.JSON_FOLDER = os.path.join(os.getcwd(), 'temp_business_data')
        
        # Define comprehensive schema for all data structures
        self.FILES_AND_STRUCTURES = {
            "comparable_companies": {
                "filename": "comparables.json",
                "root_key": "comparables",
                "description": "Stores comparable company metrics and multiples",
                "version": "1.0",
                "default_content": {
                    "comparables": [
                        {
                            "company_name": "Sample Company",
                            "enterprise_value": 100.0,
                            "market_cap": 80.0,
                            "ebitda": 10.0,
                            "equity_beta": 1.0,
                            "asset_beta": 0.8,
                            "ev_ebitda_multiple": 10.0,
                            "source": "Sample Source",
                            "source_date": "2024-01-01"
                        }
                    ]
                },
                "structure": {
                    "comparables": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "company_name",
                                "enterprise_value",
                                "market_cap", 
                                "ebitda",
                                "equity_beta",
                                "asset_beta",
                                "ev_ebitda_multiple",
                                "source",
                                "source_date"
                            ],
                            "properties": {
                                "company_name": {
                                    "type": "string",
                                    "description": "Name of the comparable company",
                                    "min_length": 1,
                                    "max_length": 100,
                                    "order": 1
                                },
                                "enterprise_value": {
                                    "type": "number",
                                    "description": "Enterprise value in millions",
                                    "minimum": 0,
                                    "order": 2
                                },
                                "market_cap": {
                                    "type": "number",
                                    "description": "Market capitalization in millions",
                                    "minimum": 0,
                                    "order": 3
                                },
                                "ebitda": {
                                    "type": "number",
                                    "description": "EBITDA in millions",
                                    "order": 4
                                },
                                "equity_beta": {
                                    "type": "number",
                                    "description": "Equity beta",
                                    "order": 5
                                },
                                "asset_beta": {
                                    "type": "number", 
                                    "description": "Asset/unlevered beta",
                                    "order": 6
                                },
                                "ev_ebitda_multiple": {
                                    "type": "number",
                                    "description": "EV/EBITDA multiple",
                                    "order": 7
                                },
                                "source": {
                                    "type": "string",
                                    "description": "Source of the comparable data",
                                    "order": 8
                                },
                                "source_date": {
                                    "type": "string",
                                    "description": "Date the comparable data was sourced",
                                    "format": "date",
                                    "order": 9
                                }
                            }
                        }
                    }
                }
            },
            "employees": {
                "filename": "employees.json", 
                "root_key": "employees",
                "description": "Stores employee information and wages",
                "version": "1.0",
                "default_content": {
                    "employees": [
                        {
                            "role": "Sample Role",
                            "number": 1,
                            "wage": 15.0,
                            "wage_type": "hourly",
                            "monthly_hours": 160,
                            "notes": "Sample employee role",
                            "source_link": "https://example.com",
                            "source_string": "Sample Source"
                        }
                    ]
                },
                "structure": {
                    "employees": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "role",
                                "number",
                                "wage",
                                "wage_type",
                                "monthly_hours", 
                                "notes",
                                "source_link",
                                "source_string"
                            ],
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "description": "Job title or role of employee",
                                    "min_length": 1,
                                    "max_length": 100,
                                    "order": 1
                                },
                                "number": {
                                    "type": "number",
                                    "description": "Number of employees in this role",
                                    "minimum": 0,
                                    "order": 2
                                },
                                "wage": {
                                    "type": "number",
                                    "description": "Wage amount (hourly or salary)",
                                    "minimum": 0,
                                    "order": 3
                                },
                                "wage_type": {
                                    "type": "string",
                                    "description": "Type of wage - hourly or salary",
                                    "enum": ["hourly", "salary"],
                                    "order": 4
                                },
                                "monthly_hours": {
                                    "type": "number",
                                    "description": "Expected monthly hours if hourly wage",
                                    "minimum": 0,
                                    "order": 5
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "Additional notes about the role",
                                    "order": 6
                                },
                                "source_link": {
                                    "type": "string",
                                    "description": "URL to wage/role source",
                                    "format": "uri",
                                    "order": 7
                                },
                                "source_string": {
                                    "type": "string",
                                    "description": "Source of wage/role information",
                                    "order": 8
                                }
                            }
                        }
                    }
                }
            },
            "operating_expenses": {
                "filename": "OPEX.json",
                "root_key": "expenses",
                "description": "Stores operating expense information",
                "version": "1.0",
                "default_content": {
                    "expenses": [
                        {
                            "expense_name": "Sample Operating Expense",
                            "amount": 1000.0,
                            "frequency": "Monthly",
                            "source_string": "Sample Source",
                            "source_link": "https://example.com",
                            "notes": "Sample operating expense"
                        }
                    ]
                },
                "structure": {
                    "expenses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "expense_name",
                                "amount",
                                "frequency",
                                "source_string",
                                "source_link",
                                "notes"
                            ],
                            "properties": {
                                "expense_name": {
                                    "type": "string",
                                    "description": "Name of the operating expense",
                                    "min_length": 1,
                                    "max_length": 100,
                                    "order": 1
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "Cost amount per occurrence",
                                    "minimum": 0,
                                    "order": 2
                                },
                                "frequency": {
                                    "type": "string",
                                    "description": "How often the expense occurs",
                                    "order": 3
                                },
                                "source_string": {
                                    "type": "string",
                                    "description": "Source of the cost information",
                                    "order": 4
                                },
                                "source_link": {
                                    "type": "string",
                                    "description": "URL to cost source",
                                    "format": "uri",
                                    "order": 5
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "Additional notes about the expense",
                                    "order": 6
                                }
                            }
                        }
                    }
                }
            },
            "historical_financials": {
                "filename": "hist_IS.json",
                "root_key": "historical_financials",
                "description": "Stores historical income statement data",
                "version": "1.0",
                "default_content": {
                    "historical_financials": [
                        {
                            "year": 2023,
                            "revenue": 1000000.0,
                            "cost_of_sales": 600000.0,
                            "operating_expenses": 200000.0,
                            "ebitda": 200000.0,
                            "depreciation": 50000.0,
                            "ebit": 150000.0,
                            "interest_expense": 10000.0,
                            "income_taxes": 35000.0,
                            "net_income": 105000.0
                        }
                    ]
                },
                "structure": {
                    "historical_financials": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "year",
                                "revenue",
                                "cost_of_sales",
                                "operating_expenses",
                                "ebitda",
                                "depreciation",
                                "ebit",
                                "interest_expense",
                                "income_taxes",
                                "net_income"
                            ],
                            "properties": {
                                "year": {
                                    "type": "number",
                                    "description": "Fiscal year",
                                    "order": 1
                                },
                                "revenue": {
                                    "type": "number",
                                    "description": "Total revenue",
                                    "minimum": 0,
                                    "order": 2
                                },
                                "cost_of_sales": {
                                    "type": "number",
                                    "description": "Direct costs of goods/services sold",
                                    "minimum": 0,
                                    "order": 3
                                },
                                "operating_expenses": {
                                    "type": "number",
                                    "description": "Operating expenses excluding depreciation",
                                    "minimum": 0,
                                    "order": 4
                                },
                                "ebitda": {
                                    "type": "number",
                                    "description": "Earnings before interest, taxes, depreciation & amortization",
                                    "order": 5
                                },
                                "depreciation": {
                                    "type": "number",
                                    "description": "Depreciation & amortization expense",
                                    "minimum": 0,
                                    "order": 6
                                },
                                "ebit": {
                                    "type": "number",
                                    "description": "Earnings before interest & taxes",
                                    "order": 7
                                },
                                "interest_expense": {
                                    "type": "number",
                                    "description": "Interest expense",
                                    "minimum": 0,
                                    "order": 8
                                },
                                "income_taxes": {
                                    "type": "number",
                                    "description": "Income tax expense",
                                    "minimum": 0,
                                    "order": 9
                                },
                                "net_income": {
                                    "type": "number",
                                    "description": "Net income",
                                    "order": 10
                                }
                            }
                        }
                    }
                }
            },
            "capital_expenditures": {
                "filename": "capex.json",
                "root_key": "expenses",
                "description": "Stores capital expenditure (CAPEX) information",
                "version": "1.0",
                "default_content": {
                    "expenses": [
                        {
                            "expense_name": "Sample Capital Expenditure",
                            "amount": 50000.0,
                            "frequency": "One-time",
                            "source_link": "https://example.com",
                            "source_string": "Sample Source",
                            "notes": "Sample capital expenditure"
                        }
                    ]
                },
                "structure": {
                    "expenses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "expense_name",
                                "amount",
                                "frequency",
                                "source_link",
                                "source_string",
                                "notes"
                            ],
                            "properties": {
                                "expense_name": {
                                    "type": "string",
                                    "description": "Name of the capital expenditure item",
                                    "min_length": 1,
                                    "max_length": 100,
                                    "order": 1
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "Cost of the capital expenditure",
                                    "minimum": 0,
                                    "order": 2
                                },
                                "frequency": {
                                    "type": "string",
                                    "description": "Frequency or timing of the expenditure",
                                    "order": 3
                                },
                                "source_link": {
                                    "type": "string",
                                    "description": "URL to source of cost information",
                                    "format": "uri",
                                    "order": 4
                                },
                                "source_string": {
                                    "type": "string",
                                    "description": "Description of the cost information source",
                                    "order": 5
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "Additional notes about the capital expenditure",
                                    "order": 6
                                }
                            }
                        }
                    }
                }
            },
            "cost_of_sales": {
                "filename": "cost_of_sales.json",
                "root_key": "cost_items",
                "description": "Stores cost of goods sold (COGS) and direct cost information",
                "version": "1.0",
                "default_content": {
                    "cost_items": [
                        {
                            "cost_item_name": "Sample Direct Cost",
                            "cost_per_unit": 10.0,
                            "cost_source": "Sample Source",
                            "cost_source_link": "https://example.com",
                            "monthly_transactions": 100,
                            "frequency_notes": "Units per month",
                            "frequency_source": "Sample Source",
                            "frequency_source_link": "https://example.com"
                        }
                    ]
                },
                "structure": {
                    "cost_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "cost_item_name",
                                "cost_per_unit",
                                "cost_source",
                                "cost_source_link",
                                "monthly_transactions",
                                "frequency_notes",
                                "frequency_source",
                                "frequency_source_link"
                            ],
                            "properties": {
                                "cost_item_name": {
                                    "type": "string",
                                    "description": "Name of the cost item or direct cost",
                                    "min_length": 1,
                                    "max_length": 100,
                                    "order": 1
                                },
                                "cost_per_unit": {
                                    "type": "number",
                                    "description": "Cost per unit/service",
                                    "minimum": 0,
                                    "order": 2
                                },
                                "cost_source": {
                                    "type": "string",
                                    "description": "Source of the cost information",
                                    "order": 3
                                },
                                "cost_source_link": {
                                    "type": "string",
                                    "description": "URL to cost source",
                                    "format": "uri",
                                    "order": 4
                                },
                                "monthly_transactions": {
                                    "type": "number",
                                    "description": "Number of transactions per month",
                                    "minimum": 0,
                                    "order": 5
                                },
                                "frequency_notes": {
                                    "type": "string",
                                    "description": "Additional notes about frequency",
                                    "order": 6
                                },
                                "frequency_source": {
                                    "type": "string",
                                    "description": "Source of frequency information",
                                    "order": 7
                                },
                                "frequency_source_link": {
                                    "type": "string",
                                    "description": "URL to frequency source",
                                    "format": "uri",
                                    "order": 8
                                }
                            }
                        }
                    }
                }
            },
            "revenue": {
                "filename": "revenue_build.json",
                "root_key": "revenue_sources",
                "description": "Stores revenue sources and pricing information",
                "version": "1.0",
                "structure": {
                    "revenue_sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "revenue_source_name",
                                "revenue_source_price",
                                "price_source",
                                "price_source_link",
                                "monthly_transactions",
                                "frequency_notes",
                                "frequency_source",
                                "frequency_source_link"
                            ],
                            "properties": {
                                "revenue_source_name": {
                                    "type": "string",
                                    "description": "Name of the revenue stream",
                                    "min_length": 1,
                                    "max_length": 100,
                                    "order": 1
                                },
                                "revenue_source_price": {
                                    "type": "number",
                                    "description": "Price per unit/service",
                                    "minimum": 0,
                                    "order": 2
                                },
                                "price_source": {
                                    "type": "string",
                                    "description": "Source of the pricing information",
                                    "order": 3
                                },
                                "price_source_link": {
                                    "type": "string",
                                    "description": "URL to pricing source",
                                    "format": "uri",
                                    "order": 4
                                },
                                "monthly_transactions": {
                                    "type": "number",
                                    "description": "Number of transactions per month",
                                    "minimum": 0,
                                    "order": 5
                                },
                                "frequency_notes": {
                                    "type": "string",
                                    "description": "Additional context about frequency",
                                    "order": 6
                                },
                                "frequency_source": {
                                    "type": "string",
                                    "description": "Source of frequency data",
                                    "order": 7
                                },
                                "frequency_source_link": {
                                    "type": "string",
                                    "description": "URL to frequency source",
                                    "format": "uri",
                                    "order": 8
                                }
                            }
                        }
                    }
                },
                "default_content": {
                    "revenue_sources": [
                        {
                            "revenue_source_name": "Sample Revenue Stream",
                            "price": 25.00,
                            "price_source": "Industry Average",
                            "price_source_link": "https://example.com/pricing",
                            "monthly_transactions": 100,
                            "frequency_notes": "Transactions per day",
                            "frequency_source": "Market Research",
                            "frequency_source_link": "https://example.com/research"
                        }
                    ]
                }
            }
        }

        # Define structures for Catalyst project
        self.CATALYST_FILES_AND_STRUCTURES = {
            "fundamentals": {
                "filename": "fundamentals.json",
                "root_key": "fundamentals",
                "description": "Stores basic firm information",
                "version": "1.0",
                "default_content": {
                    "fundamentals": [
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
                    ]
                }
            },
            "investment_team": {
                "filename": "investment_team.json",
                "root_key": "team_members",
                "description": "Stores investment team information",
                "version": "1.0",
                "default_content": {
                    "team_members": [
                        {
                            "investment_team_member_name": "Placeholder Name",
                            "investment_team_member_title": "Placeholder Title",
                            "investment_team_member_join_date": 2020,
                            "source_string": "Placeholder Source",
                            "source_link": "https://example.com"
                        }
                    ]
                }
            },
            "fees_key_terms": {
                "filename": "fees_key_terms.json",
                "root_key": "terms",
                "description": "Stores fund terms and fee structures",
                "version": "1.0",
                "default_content": {
                    "terms": [
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
                    ]
                }
            },
            "seed_terms": {
                "filename": "seed_terms.json",
                "root_key": "investments",
                "description": "Stores seed investment terms",
                "version": "1.0",
                "default_content": {
                    "investments": [
                        {
                            "expense_name": "Target Seed Investment Placeholder",
                            "initial_investment": "Initial Seed Investment Placeholder",
                            "fundraising_date": "Placeholder Date",
                            "revenue_share": "0%",
                            "revenue_share_cap": "0.0x",
                            "revenue_share_tail": "0%",
                            "source_string": "Placeholder Source",
                            "source_link": "https://example.com"
                        }
                    ]
                }
            },
            "deal_history": {
                "filename": "deal_history.json",
                "root_key": "deals",
                "description": "Stores historical deal information",
                "version": "1.0",
                "default_content": {
                    "deals": [
                        {
                            "date": "Placeholder Date",
                            "firm": "Placeholder Firm",
                            "amount": "$0",
                            "realized": "No",
                            "syndicate_partners": "Placeholder Partners",
                            "source_string": "Placeholder Source",
                            "source_link": "https://example.com"
                        }
                    ]
                }
            },
            "service_providers": {
                "filename": "service_providers.json",
                "root_key": "providers",
                "description": "Stores service provider information",
                "version": "1.0",
                "default_content": {
                    "providers": [
                        {
                            "service_type": "Placeholder Service",
                            "firm_name": "Placeholder Firm",
                            "source_string": "Placeholder Source",
                            "source_link": "https://example.com"
                        }
                    ]
                }
            }
        }



    def initialize_json_files(self, project_name):
        # Create temp directory if it doesn't exist
        if not os.path.exists(self.JSON_FOLDER):
            try:
                os.makedirs(self.JSON_FOLDER)
                logging.info(f"Created directory: {self.JSON_FOLDER}")
            except Exception as e:
                logging.error(f"Failed to create directory {self.JSON_FOLDER}: {e}")
                return False
                
        # Delete any existing files
        try:
            for filename in os.listdir(self.JSON_FOLDER):
                file_path = os.path.join(self.JSON_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logging.info(f"Deleted existing file: {filename}")
        except Exception as e:
            logging.error(f"Error cleaning directory {self.JSON_FOLDER}: {e}")
            return False
            
        # Create new files with default content for both project types
        success = True
        
        # Initialize financial files
        for table_name, file_info in self.FILES_AND_STRUCTURES.items():
            file_path = os.path.join(self.JSON_FOLDER, file_info["filename"])
            try:
                if "default_content" in file_info:
                    initial_data = file_info["default_content"][file_info["root_key"]]
                else:
                    initial_data = {file_info["root_key"]: []} if "root_key" in file_info else []
                
                with open(file_path, 'w') as json_file:
                    json.dump(initial_data, json_file, indent=4)
                logging.info(f"Created financial file with default content: {file_info['filename']}")
            except Exception as e:
                logging.error(f"Failed to create {file_path}: {e}")
                success = False

        # Initialize catalyst files  
        for table_name, file_info in self.CATALYST_FILES_AND_STRUCTURES.items():
            file_path = os.path.join(self.JSON_FOLDER, file_info["filename"])
            try:
                if "default_content" in file_info:
                    initial_data = file_info["default_content"][file_info["root_key"]]
                else:
                    initial_data = {file_info["root_key"]: []} if "root_key" in file_info else []
                
                with open(file_path, 'w') as json_file:
                    json.dump(initial_data, json_file, indent=4)
                logging.info(f"Created catalyst file with default content: {file_info['filename']}")
            except Exception as e:
                logging.error(f"Failed to create {file_path}: {e}")
                success = False
        
        return success

    def load_json_data(self, identifier, project_name="financial"):
        """
        Load and process JSON data from files based on identifier.
        
        Args:
            identifier (str): Table/file identifier to load
            project_name (str): Project type - "financial" or "catalyst"
            
        Returns:
            dict/list: Processed JSON data based on identifier type
            None: If any error occurs during loading/processing
        """
        # Select appropriate file structures based on project
        files_and_structures = self.CATALYST_FILES_AND_STRUCTURES if project_name == "catalyst" else self.FILES_AND_STRUCTURES
        # Get filename and validate schema
        file_info = None
        if identifier in files_and_structures:
            # Direct match found
            file_info = files_and_structures[identifier]
        else:
            # Search for partial match in table names
            for table_name, info in files_and_structures.items():
                if identifier in table_name.lower():
                    file_info = info
                    break
        
        if not file_info:
            logging.error(f"load_json_data: No matching schema found for identifier: {identifier}")
            return None
            
        # Load JSON file
        file_path = os.path.join(self.JSON_FOLDER, files_and_structures[identifier]["filename"])
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                logging.info(f"load_json_data: Successfully loaded data for {identifier}")
        except FileNotFoundError:
            logging.error(f"load_json_data: File not found at path: {file_path}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"load_json_data: JSON parsing error for {file_path}: {e}")
            return None
        except Exception as e:
            logging.error(f"load_json_data: Unexpected error loading {file_path}: {e}")
            return None

        # Get the root key from file_info
        root_key = file_info.get("root_key")

        # Return the data under the root key
        try:
            # For all tables, return the data under the root key if it exists
            if root_key:
                return data.get(root_key, [])
            return data
                
        except Exception as e:
            logging.error(f"load_json_data: Error processing data for {identifier}: {e}. Data is {data}")
            return None



    def load_json_explanation(self, table_name, project_name):
        """Load explanation text for a given table"""
        # Check if table exists in FILES_AND_STRUCTURES
        if table_name not in self.FILES_AND_STRUCTURES:
            logging.error(f"load_json_explanation: Invalid table name: {table_name}")
            return "No explanation available."

        # Get filename from FILES_AND_STRUCTURES
        file_info = self.FILES_AND_STRUCTURES[table_name]
        base_filename = file_info["filename"].replace(".json", "")
        explanation_file = f"{base_filename}_explanation.txt"
        
        # Determine project folder
        project_folder = "catalyst" if project_name == "catalyst" else "fin_model"
        
        file_path = os.path.join(EXPLANATION_FILES_DIR, project_folder, explanation_file)
        
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"load_json_explanation: Explanation file not found at path: {file_path}")
            return "No explanation available."
        except Exception as e:
            logging.error(f"load_json_explanation: Error reading explanation file: {e}")
            return "No explanation available."

    def update_json_files(self, json_data, project_name):
        """Update JSON files with new data"""
        # Get the appropriate file structure mapping based on project
        file_structure = self.CATALYST_FILES_AND_STRUCTURES if project_name == "catalyst" else self.FILES_AND_STRUCTURES
        
        if not file_structure:
            logging.error(f"update_json_files: No file structure found for project: {project_name}")
            return
            
        for table_name, new_data in json_data.items():
            # Get file info from structure
            file_info = file_structure.get(table_name)
            if not file_info:
                logging.warning(f"update_json_files: No file info found for table: {table_name} in project {project_name}")
                continue
                
            file_name = file_info.get("filename")
            if not file_name:
                logging.warning(f"update_json_files: No filename found for table: {table_name}")
                continue

            file_path = os.path.join(self.JSON_FOLDER, file_name)

            try:
                with open(file_path, "w") as json_file:
                    json.dump(new_data, json_file, indent=4)
                logging.info(f"update_json_files: Successfully updated {file_name} for project {project_name}")
            except Exception as e:
                logging.error(f"update_json_files: Failed to update {file_name} for project {project_name}: {e}")

    def fix_incomplete_json(self, json_string):
        """Fix incomplete JSON by adding missing brackets"""
        open_curly = json_string.count('{')
        close_curly = json_string.count('}')
        open_square = json_string.count('[')
        close_square = json_string.count(']')

        if open_curly > close_curly:
            json_string += '}' * (open_curly - close_curly)
        if open_square > close_square:
            json_string += ']' * (open_square - close_square)

        return json_string

    def save_json_to_file(self, json_data):
        """Save JSON data to a timestamped file"""
        os.makedirs(self.JSON_FOLDER, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"openai_response_{timestamp}.json"
        file_path = os.path.join(self.JSON_FOLDER, file_name)

        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

        logging.info(f"save_json_to_file: Saved JSON response to {file_path}")