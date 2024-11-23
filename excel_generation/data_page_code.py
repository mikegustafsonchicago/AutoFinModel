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
        
        for direct_cost in self.business_object.cost_of_sales_items:
            # Write the headers
            headers = ["Cost Item Name", "Cost per Unit", "Cost Source", "Cost Source Link",
                      "Frequency", "Frequency Notes", "Frequency Source", "Frequency Source Link"]
            for i, header in enumerate(headers):
                self.write_to_sheet(row, i+col_offset, header, format_name="underline")
            row += 1
            
            # Write cost item data
            self.write_to_sheet(row, col_offset, direct_cost['cost_item_name'])
            self.write_to_sheet(row, col_offset+1, direct_cost['cost_per_unit'], format_name="currency_cents")
            self.write_to_sheet(row, col_offset+2, direct_cost['cost_source'])
            self.write_to_sheet(row, col_offset+3, direct_cost['cost_source_link'])
            self.write_to_sheet(row, col_offset+4, direct_cost['frequency'], format_name="number")
            self.write_to_sheet(row, col_offset+5, direct_cost['frequency_notes'])
            self.write_to_sheet(row, col_offset+6, direct_cost['frequency_source'])
            self.write_to_sheet(row, col_offset+7, direct_cost['frequency_source_link'])
            
            # Save reference to cost per unit cell for this cost item
            self.cell_manager.add_cell_reference(self.sheet_name, direct_cost['cost_item_name'], 
                                               row=row, col=col_offset+1)
            
            row += 2