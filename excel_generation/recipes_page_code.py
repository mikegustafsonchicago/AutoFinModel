# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:18:51 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
from cellManager import CellManager

#Create a recipes and Ingredients Sheet
class RecipesPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        
        # Storing recipe data
        # Structure:
        # {
        #   'recipe_name': {             # The key is the name of the recipe (e.g., 'Latte', 'Espresso')
        #       'ingredients': {         # A dictionary of ingredients with quantities
        #           'ingredient_name': float  # The quantity of the ingredient required for this recipe
        #       },
        #       'steps': list            # A list of steps to make the recipe
        #   }
        # }
        
        # Example:
        # recipes_data = {
        #   'Latte': {
        #       'ingredients': {
        #           'Coffee': 1.5,     # 1.5 units of Coffee
        #           'Milk': 2.0        # 2.0 units of Milk
        #       },
        #       'steps': [
        #           'Brew coffee',
        #           'Steam milk',
        #           'Mix ingredients'
        #       ]
        #   }
        # }
        
        
        self.sheet_name = 'Recipes'
        self.workbook_manager=workbook_manager
        self.business_object = business_object
        self.cell_manager = cell_manager
        self.num_forecasted_years=workbook_manager.num_forecasted_years
        
        #Make the sheet
        self.recipes_sheet = workbook_manager.add_sheet(self.sheet_name)
        
        self.populate_sheet()

    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.recipes_sheet, row, col, formula_string, format_name, print_formula)
        
    def populate_sheet(self):
        #Set column widths
        self.recipes_sheet.set_column('A:A', 5)
        self.recipes_sheet.set_column('B:B', 20)
        self.recipes_sheet.set_column('C:C', 15)
        self.recipes_sheet.set_column('D:D', 10)
        self.recipes_sheet.set_column('E:E', 15)
        self.recipes_sheet.set_column('G:G', 15)
        self.recipes_sheet.set_column('H:H', 60)
        
        #Page Title
        self.write_to_sheet( 1, 1, "Recipes", format_name="title")
        
        # Create the color banner row
        self.recipes_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet( 2, col, "", format_name="color_banner")
    
        #Write the headers
        row=4
        col=1
        self.recipes_sheet.set_row(row, 30) #Set the header height to 2x normal cell height
        for label in ["Recipe Name", "Ingredient Names", "Ingredient Amounts", "Unit", "Price", "Purchase Scaling Value", "Assumptions/Notes"]:
            self.write_to_sheet( row, col, label, format_name="bottom_border_wrap")
            col+=1
    
        
        # Write some data to cells
        row=5
        col=1
    
        for recipe_dict in self.business_object.sales_recipes:
            #Iterate through the dict of recipes. The key is its name (eg large_black_coffee), the value is the actual recipe.
            self.write_to_sheet(row, col, recipe_dict['name'])
            self.write_to_sheet(row, col+4, recipe_dict['price'], format_name="currency_input_cents")
            self.cell_manager.add_cell_reference(self.sheet_name, recipe_dict['name'], 'price', row=row, col=col+4) #Save the location of the price
            self.write_to_sheet(row, col+5, 1/(len(self.business_object.sales_recipes)), format_name="percent_input")
            self.cell_manager.add_cell_reference(self.sheet_name, recipe_dict['name'], 'customer_fraction', row=row, col=col+5) #Save the location of the price
            row+=1
            for recipe_ingredient in recipe_dict["ingredients"]:
                #Iterate through the list of ingredients. These are NOT the Ingredient class, which is more robust.
                
                #This data is pulled from the recipe
                self.write_to_sheet(row, col+2, recipe_ingredient['amount'], format_name="input")
                self.write_to_sheet(row, col+3, recipe_ingredient['unit'], format_name="input")
                
                
                #The ingredient name is pulled from the linked Ingredient instance if available, else it uses the name in the recipe
                ingredient_class_instance = self.business_object.get_ingredient_by_id(recipe_ingredient['ingredient_id'])
                if ingredient_class_instance: #If there's a linked Ingredient for this line in the recipe
                    #Write the ingredient name using the name from the Ingredient class    
                    self.write_to_sheet(row, col+1, ingredient_class_instance.name) 
                    
                    #Get the price from the page of ingredient data
                    reference_cell = self.cell_manager.get_cell_reference("Data", ingredient_class_instance.name, format_type='cell_ref')#Find the cell location
                    formula_string = f'=Data!{reference_cell}*{get_cell_identifier(row, col+2)}'
                    self.write_to_sheet(row, col+4, formula_string, format_name="currency_cross_cents")
                    self.write_to_sheet(row, col+6, f"Used average price for {ingredient_class_instance.name}. See Data sheet.")
                    
                else: #If there isn't a linked instance of the Ingredient class
                    self.write_to_sheet(row, col+1, recipe_ingredient['ingredient_name']) #Use the name from the recipe input
                    self.write_to_sheet(row, col+4, recipe_ingredient['price'], format_name="currency_input_cents") #Use the price from the recipe input
                    self.write_to_sheet(row, col+6, recipe_ingredient['notes'])
                row+=1
                
            #Now sum all the ingredient costs into a total line
            self.write_to_sheet(row, col+1, "", format_name = "sum_line_cents") #Extend the top border left of the total cost
            self.write_to_sheet(row, col+2, "", format_name = "sum_line_cents") #Extend the top border left of the total cost
            self.write_to_sheet(row, col+3, "Total Cost", format_name = "sum_line_cents")
            sum_start_cell = get_cell_identifier(row-len(recipe_dict["ingredients"]), col+4)
            sum_end_cell = get_cell_identifier(row-1, col+4)
            formula_string = f"=sum({sum_start_cell}:{sum_end_cell})"
            self.write_to_sheet(row, col+4, formula_string, format_name = "sum_line_cents")
            self.cell_manager.add_cell_reference(self.sheet_name, recipe_dict['name'], 'cost', row=row, col=col+4) 
            row+=2
