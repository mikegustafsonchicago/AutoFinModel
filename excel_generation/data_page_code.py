# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:21:07 2024

@author: mikeg
"""
from helper_functions import number_to_column_letter, get_cell_identifier
from workbook_sheet_manager_code import SheetManager

class DataPage(SheetManager):
    def __init__(self, workbook_manager, cell_manager, business_object):
        super().__init__(workbook_manager, business_object, "Data")
        
        self.populate_sheet()
        
    def populate_sheet(self):
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5)   # Margin column
        self.xlsxwriter_sheet.set_column('B:B', 25)  # Cost Item Name
        self.xlsxwriter_sheet.set_column('C:C', 15)  # Cost per Unit 
        self.xlsxwriter_sheet.set_column('D:D', 12)  # Frequency
        self.xlsxwriter_sheet.set_column('E:E', 20)  # Frequency Notes
        self.xlsxwriter_sheet.set_column('F:F', 35)  # Cost Source (URL)
        self.xlsxwriter_sheet.set_column('G:G', 35)  # Frequency Source (URL)
        
        #Write the page title
        self.write_to_sheet( 1, 1, 'Raw Data Page', format_name='title')
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet( 2, col, "", format_name="color_banner")
        
        row = 5
        col_offset = 1
        
        self.write_to_sheet( row-1, 1, "Inputs", format_name="bold")
        
        for direct_cost in self.business_object.cost_of_sales_items:
            # Write the headers
            headers = ["Cost Item Name", "Cost per Unit", "Frequency", "Frequency Notes", 
                      "Cost Source", "Frequency Source"]
            for i, header in enumerate(headers):
                self.write_to_sheet(row, i+col_offset, header, format_name="underline")
            row += 1
            
            # Write cost item data
            self.write_to_sheet(row, col_offset, direct_cost['cost_item_name'])
            self.write_to_sheet(row, col_offset+1, direct_cost['cost_per_unit'], format_name="currency_cents")
            self.write_to_sheet(row, col_offset+2, direct_cost['frequency'], format_name="number")
            self.write_to_sheet(row, col_offset+3, direct_cost['frequency_notes'])
            # Add cost source as link
            self.write_to_sheet(row, col_offset+4, f'=HYPERLINK("{direct_cost["cost_source_link"]}", "{direct_cost["cost_source"]}")', is_formula=True)
            # Add frequency source as link  
            self.write_to_sheet(row, col_offset+5, f'=HYPERLINK("{direct_cost["frequency_source_link"]}", "{direct_cost["frequency_source"]}")', is_formula=True)
            
            # Save reference to cost per unit cell for this cost item
            self.cell_manager.add_cell_reference(self.sheet_name, direct_cost['cost_item_name'],
                                               row=row, col=col_offset+1)
            
            row += 2