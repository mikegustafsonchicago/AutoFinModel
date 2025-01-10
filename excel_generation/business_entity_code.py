# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 10:02:46 2024

@author: mikeg
"""
import sys
import logging
from datetime import datetime
from ingredients_code import Ingredient
import json
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from json_manager import JsonManager

class BusinessEntity:
    def __init__(self, project_type):
        self.sales_recipes = {}
        self.ingredients_list = []
        self.store_hours = 8
        self.open_days = 30
        self.customer_frequency = 2
        self.unique_ingredient_id_counter = 100
        self.placeholder_value = "9.99"
        
        # Initialize paths and JsonManager
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.path = os.path.join(base_dir, 'temp_business_data') + "/"
        self.json_manager = JsonManager()
        
        # Define file mappings for different project types
        self.file_mappings = {
            "financials": {
                "revenue_sources": "revenue",
                "cost_of_sales_items": "cost_of_sales",
                "operating_expenses": "operating_expenses",
                "capex_items": "capital_expenses",  # Updated from capital_expenditures
                "employees": "employees",
                "historical_financials": "historical_financials",
                "comparables_valuation": "comparable_companies"  # Updated from comparables_valuation
            },
            "catalyst": {
                "fundamentals": "fundamentals",
                "investment_team": "investment_team",
                "seed_terms": "seed_terms",
                "fees_key_terms": "fees_key_terms",
                "deal_history": "deal_history",
                "service_providers": "service_providers"
            },
            "fund_analysis":{
                "fundamentals": "FUND_ANALYSIS_fundamentals",
                "investment_team": "FUND_ANALYSIS_investment_team", 
                "seed_terms": "FUND_ANALYSIS_seed_terms",
                "fees_key_terms": "FUND_ANALYSIS_fees_key_terms",
                "deal_history": "FUND_ANALYSIS_deal_history",
                "service_providers": "FUND_ANALYSIS_service_providers"
            }
        }
        
        # Load project data based on type
        if project_type in self.file_mappings:
            self._load_project_data(project_type)
        else:
            logging.error(f"BusinessEntity: Invalid project type: {project_type}")

    def _load_project_data(self, project_type):
        """Load all JSON files for the specified project type with error handling."""
        for attr_name, file_name in self.file_mappings[project_type].items():
            try:
                data = self.json_manager.load_json_data(file_name)
                setattr(self, attr_name, data if data else [])
                logging.debug(f"Loaded {file_name} data successfully")
            except Exception as e:
                logging.error(f"Failed to load {file_name}: {str(e)}")
                setattr(self, attr_name, [])
        
        # Set start year if historical financials exist
        if project_type == "financials":
            self._set_start_year()

    def _set_start_year(self):
        """Set the start year based on historical financials."""
        try:
            if hasattr(self, 'historical_financials') and self.historical_financials:
                years = [entry.get("year") for entry in self.historical_financials if "year" in entry]
                self.start_year = min(years) if years else datetime.now().year
            else:
                self.start_year = datetime.now().year
        except Exception as e:
            logging.error(f"Error setting start year: {str(e)}")
            self.start_year = datetime.now().year

    def create_missing_ingredient(self, ingredient_id):
        """Create an Ingredient instance for a missing ingredient and add it to the dictionary."""
        ingredient_name = f"Unknown Ingredient (ID: {ingredient_id})"
        new_ingredient = Ingredient(ingredient_name)
        new_ingredient.ingredient_id = ingredient_id
        self.ingredients_dict[ingredient_id] = new_ingredient
        return new_ingredient

    def assign_placeholder_price(self, ingredient):
        """Assign a placeholder price for ingredients without price data."""
        if not ingredient.price_data_raw:
            return self.placeholder_value  # Default placeholder price
        else:
            return ingredient.price_data_raw[0].get('price', self.placeholder_value)
        
    def get_ingredient_by_id(self, ingredient_id):
        """Fetch an ingredient by its ID, or return None with a warning if not found."""
        ingredient=None
        for item in self.ingredients_list:
            if item.unique_id == ingredient_id:
                ingredient = item
        return ingredient
    
    def assign_unique_id(self):
        """Generate and return a unique ingredient ID."""
        unique_id = self.unique_ingredient_id_counter
        self.unique_ingredient_id_counter += 1
        return unique_id
