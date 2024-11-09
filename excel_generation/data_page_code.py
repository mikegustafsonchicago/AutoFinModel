# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:21:07 2024

@author: mikeg
"""
from helper_functions import number_to_column_letter, get_cell_identifier

class DataPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.sheet_name='Data'
        self.workbook=workbook_manager.workbook
        self.num_forecasted_years=workbook_manager.num_forecasted_years
        
        self.workbook_manager.cell_info[self.sheet_name]={}
        
        #Create the sheet
        self.data_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        self.populate_sheet()
        
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False, is_formula=False):
        self.workbook_manager.validate_and_write(self.data_sheet, row, col, formula_string, format_name, print_formula)
    
    def populate_sheet(self):
        #Set column widths
        self.data_sheet.set_column('A:A', 5)  # Set width of column A to 10 units
        self.data_sheet.set_column('B:B', 30)  # Set width of column A to 10 units
        self.data_sheet.set_column('F:F', 30)  # Set width of column A to 10 units
        self.data_sheet.set_column('G:G', 30)  # Set width of column A to 10 units
        
        #Write the page title
        self.write_to_sheet( 1, 1, 'Raw Data Page', format_name='title')
        
        # Create the color banner row
        self.data_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet( 2, col, "", format_name="color_banner")
        
        row = 5
        col_offset = 1
        
        self.write_to_sheet( row-1, 1, "Inputs", format_name="bold")
        
        for ingredient in self.business_object.ingredients_list:
            #Write the headers for each ingredient
            for item in enumerate(ingredient.price_data_raw[0].keys()): 
                self.write_to_sheet( row, item[0]+col_offset, item[1], format_name="underline")
            row+=1
            
            for line in enumerate(ingredient.price_data_raw):
                #Ingredient info
                for item in enumerate(line[1].keys()):
                    if item[1] == "price":
                        self.write_to_sheet( row, item[0]+col_offset, line[1][item[1]], format_name="currency_cents")
                    elif item[1] =="selling_quantity":
                        self.write_to_sheet( row, item[0]+col_offset, float(line[1][item[1]]), format_name="number")
                    else:
                        self.write_to_sheet( row, item[0]+col_offset, line[1][item[1]])
                row+=1
            self.write_to_sheet( row, 1, f'Average price per {ingredient.base_unit}', format_name="sum_line_cents")
            range_row_start=row-len(ingredient.price_data_raw)
            range_row_end=row-1
            price_col= col_offset+1
            quantity_col = col_offset+2
            unit_col = col_offset+3
            price_range = f"{get_cell_identifier(range_row_start, price_col)}:{get_cell_identifier(range_row_end, price_col)}"
            quantity_range = f"{get_cell_identifier(range_row_start, quantity_col)}:{get_cell_identifier(range_row_end, quantity_col)}"
            unit_range = f"{get_cell_identifier(range_row_start, unit_col)}:{get_cell_identifier(range_row_end, unit_col)}"
            formula_string = f'{{=AVERAGE(IF({unit_range}="{ingredient.base_unit}", {price_range}/{quantity_range}))}}'
            self.write_to_sheet(row, col_offset+1, formula_string, format_name="sum_line_cents") #Write the cell that gives average unit cost
            self.cell_manager.add_cell_reference(self.sheet_name, ingredient.name, row=row, col=col_offset+1)#Save the cell location
            row+=2
            