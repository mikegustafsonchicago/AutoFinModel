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
    def __init__(self, project_name):
        self.sales_recipes={}
        self.ingredients_list = []
        self.store_hours = 8 #Hours open per day
        self.open_days = 30 #Days open per month
        self.customer_frequency = 2 #Customers/hour
        self.unique_ingredient_id_counter = 100  # Start ID count from 100 to avoid conflicts
        self.placeholder_value = "9.99"
        
        # Adjust path to move up one directory level from the current file location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.path.join(base_dir, 'sample_jsons') + "/"
        self.path = os.path.join(base_dir, 'temp_business_data') + "/"
       
        # Initialize JsonManager
        self.json_manager = JsonManager()
        
        # Load "financials" project data from JSON files
        if project_name == "financials":
            self.revenue_sources = self.json_manager.load_json_data("revenue")
            self.revenue_sources = self.revenue_sources if self.revenue_sources else []
            self.cost_of_sales_items = self.json_manager.load_json_data("cost_of_sales") 
            self.cost_of_sales_items = self.cost_of_sales_items if self.cost_of_sales_items else []
            self.operating_expenses = self.json_manager.load_json_data("operating_expenses")
            self.operating_expenses = self.operating_expenses if self.operating_expenses else []
            self.capex_items = self.json_manager.load_json_data("capital_expenditures")
            self.capex_items = self.capex_items if self.capex_items else []
            self.employees = self.json_manager.load_json_data("employees")
            self.employees = self.employees if self.employees else []
            self.hist_IS = self.json_manager.load_json_data("historical_financials")
            self.hist_IS = self.hist_IS if self.hist_IS else []
            self.comparables_valuation = self.json_manager.load_json_data("comparables")
            self.comparables_valuation = self.comparables_valuation if self.comparables_valuation else []
       
            # Get earliest year from historical financials, default to current year if no data
            if self.hist_IS:
                years = [entry["year"] for entry in self.hist_IS]
                self.start_year = min(years) if years else datetime.now().year
            else:
                self.start_year = datetime.now().year
               
        #CATALYST Loads
        elif project_name == "catalyst":
            self.fundamentals = self.json_manager.load_json_data("fundamentals", project_name="catalyst")
            self.fundamentals = self.fundamentals if self.fundamentals else []
            self.investment_team = self.json_manager.load_json_data("investment_team", project_name="catalyst")
            self.investment_team = self.investment_team if self.investment_team else []
            self.seed_terms = self.json_manager.load_json_data("seed_terms", project_name="catalyst")
            self.seed_terms = self.seed_terms if self.seed_terms else []
            self.fees_key_terms = self.json_manager.load_json_data("fees_key_terms", project_name="catalyst")
            self.fees_key_terms = self.fees_key_terms if self.fees_key_terms else []
            self.deal_history = self.json_manager.load_json_data("deal_history", project_name="catalyst")
            self.deal_history = self.deal_history if self.deal_history else []
            self.service_providers = self.json_manager.load_json_data("service_providers", project_name="catalyst")
            self.service_providers = self.service_providers if self.service_providers else []
        
        else:
            logging.error(f"BusinessEntity: Invalid project name: {project_name}")


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
