# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 10:02:46 2024

@author: mikeg
"""
import sys
from ingredients_code import Ingredient
import json
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from json_manager import load_json_file

class BusinessEntity:
    def __init__(self):
        self.sales_recipes={}
        self.ingredients_list = []
        self.store_hours = 8 #Hours open per day
        self.open_days = 30 #Days open per month
        self.customer_frequency = 2 #Customers/hour
        self.unique_ingredient_id_counter = 100  # Start ID count from 100 to avoid conflicts
        
        # Adjust path to move up one directory level from the current file location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        os.path.join(base_dir, 'sample_jsons') + "/"
        self.path = os.path.join(base_dir, 'temp_business_data') + "/"
       
        # Load data from JSON files
        self.sales_recipes = load_json_file("revenue")
        self.ingredients_list = load_json_file("purchases")
        self.operating_expenses = load_json_file("opex")
        self.capex_items = load_json_file("capex")
        self.employees = load_json_file("employees")
        self.financials = load_json_file("financials")
        self.comparables_valuation = load_json_file("comparables")


        self.placeholder_value = "9.99"
        self.start_year=1998
        
        
        #CATALYST Loads
        self.fundamentals = load_json_file("fundamentals")
        self.investment_team = load_json_file("investmentTeam") 
        self.seed_terms = load_json_file("seedTerms")
        self.fees_key_terms = load_json_file("feesKeyTerms")
        self.deal_history = load_json_file("dealHistory")
        self.service_providers = load_json_file("serviceProviders")
        
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
    
    
    
       

        
