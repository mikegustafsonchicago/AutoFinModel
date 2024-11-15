# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 10:02:46 2024

@author: mikeg
"""

from ingredients_code import Ingredient
import json
import os

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
        self.load_recipes_from_json(self.path+'recipes.json')
        self.load_ingredients_from_json(self.path+'ingredients.json')
        self.load_operating_expenses_from_json(self.path+'OPEX.json') #Load OPEX data
        self.load_capex_from_json(self.path+'CAPEX.json')  # Load CAPEX data
        self.load_employees_from_json(self.path+'employees.json')  # Load Employee data
        self.load_historical_financials(self.path+'financials.json')  # Load Employee data
        self.load_valuation_comps_from_json(self.path+'comparables.json') #Load the comparables data
        self.placeholder_value = "9.99"
        self.start_year=1998
        
        
        #CATALYST Loads
        self.load_fundamentals_from_json(self.path + 'fundamentals.json')
        self.load_investment_team_from_json(self.path + 'investment_team.json')
        self.load_seed_terms_from_json(self.path + 'seed_terms.json')
        self.load_fees_key_terms_from_json(self.path + 'fees_key_terms.json')
        
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
    
    def load_recipes_from_json(self, filepath):
        """Load recipes from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                recipes_data = json.load(file)

                # Dynamically load all recipes into sales_recipes
                self.sales_recipes = recipes_data['recipes']  # Assuming recipes_data is already in the proper format

                print(f"Successfully loaded {len(recipes_data)} recipes from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Recipe load error. Error parsing JSON: {e}")
    
            
    def load_ingredients_from_json(self, filepath):
        """Load ingredients from JSON file and instantiate Ingredient objects."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                for ingredient_item in data['purchases_table']:
                    # Create Ingredient instance
                    ingredient = Ingredient(
                        name=ingredient_item['ingredient_name'],
                        ingredient_id=ingredient_item['ingredient_id'],
                        price_data_raw=ingredient_item['price_data_raw']
                    )
                    
                    # Assign the ingredient_id and add to ingredients_dict
                    #ingredient_id = ingredient_item.get('ingredient_id', None)
                    if ingredient.unique_id:
                        self.ingredients_list.append(ingredient)
                    else:
                        print(f"Warning: Ingredient {ingredient.name} is missing an ID.")

            print("Successfully loaded ingredients from JSON.")

        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
    
    def load_operating_expenses_from_json(self, filepath):
        """Load operating expenses from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.operating_expenses = data['expenses']
                print(f"Successfully loaded {len(self.operating_expenses)} operating expenses from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            
    
    def load_capex_from_json(self, filepath):
        """Load CAPEX (Capital Expenditures) data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.capex_items = data['expenses']  # Collect all capex items
                print(f"Successfully loaded {len(self.capex_items)} CAPEX items from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            
    def load_employees_from_json(self, filepath):
        """Load employee data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.employees = data['employees']
                print(f"Successfully loaded {len(self.employees)} employees from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")

    def load_historical_financials(self, filepath):
        """Load historical financial data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.financials = data
                print(f"Successfully loaded financial data for {len(self.financials)} years.")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
    
    def load_valuation_comps_from_json(self, filepath):
        """Load benchmarking and valuation data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.comparables_valuation = data
                print(f"Successfully loaded benchmarking and valuation data from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            
            
#----------CATALYST PARTNERS LOAD FUNCTIONS

    def load_fundamentals_from_json(self, filepath):
        """Load fundamentals data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.fundamentals = data  # Store the entire list as fundamentals
                print(f"Successfully loaded {len(data)} fundamentals records from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing fundamentals JSON: {e}")
    
    def load_investment_team_from_json(self, filepath):
        """Load investment team data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.investment_team = data  # Store the entire list as investment team
                print(f"Successfully loaded {len(data)} investment team members from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing investment team JSON: {e}")


    def load_seed_terms_from_json(self, filepath):
        """Load seed terms data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.seed_terms = data  # Store the entire list as seed terms
                print(f"Successfully loaded {len(data)} seed terms from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing seed terms JSON: {e}")


    def load_fees_key_terms_from_json(self, filepath):
        """Load fees and key terms data from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                self.fees_key_terms = data  # Store the entire list as fees and key terms
                print(f"Successfully loaded {len(data)} fees and key terms from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing fees and key terms JSON: {e}")


        
