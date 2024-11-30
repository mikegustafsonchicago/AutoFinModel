# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:24:25 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
from workbook_sheet_manager_code import SheetManager
class TitlePage(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
        

        self.populate_sheet()
            
    def populate_sheet(self):
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5)
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet( 2, col, "", format_name="color_banner")
        
        self.write_to_sheet( 1, 1, "Urban Brew Financial Model", format_name="title")
        
        #Insert the shop logo
        self.xlsxwriter_sheet.insert_image('B5', 'logo.png', {'x_scale': 0.3, 'y_scale': 0.3})
        

