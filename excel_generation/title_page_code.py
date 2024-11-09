# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:24:25 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier

class TitlePage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object

        #Create the sheet
        self.sheet_name = 'Title_Page'
        self.workbook_manager.cell_info[self.sheet_name]={}
        self.title_sheet = workbook_manager.add_sheet(self.sheet_name)
        self.populate_sheet()
    
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False, is_formula=False):
        self.workbook_manager.validate_and_write(self.title_sheet, row, col, formula_string, format_name, print_formula)
            
    def populate_sheet(self):
        #Set column widths
        self.title_sheet.set_column('A:A', 5)
        
        # Create the color banner row
        self.title_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet( 2, col, "", format_name="color_banner")
        
        self.write_to_sheet( 1, 1, "Urban Brew Financial Model", format_name="title")
        
        #Insert the shop logo
        self.title_sheet.insert_image('B5', 'logo.png', {'x_scale': 0.3, 'y_scale': 0.3})
        
