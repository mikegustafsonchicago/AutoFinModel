# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 14:16:06 2024

@author: mikeg
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:18:51 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
from cellManager import CellManager
import logging

#Create a recipes and Ingredients Sheet
class ComparablesQuantPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
       
        self.workbook_manager = workbook_manager
        self.business_object = business_object
        self.cell_manager = cell_manager
        self.num_forecasted_years=workbook_manager.num_forecasted_years
        self.sheet_name = 'Valuation Comps'
        self.quant_comps_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        
        #Make the sheet
        self.populate_sheet()

    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.quant_comps_sheet, row, col, formula_string, format_name, print_formula)
        
    def populate_sheet(self):
        #Set column widths
        self.quant_comps_sheet.set_column('A:A', 5)
        self.quant_comps_sheet.set_column('B:B', 20)
        self.quant_comps_sheet.set_column('C:C', 15)
        self.quant_comps_sheet.set_column('D:D', 10)
        self.quant_comps_sheet.set_column('E:J', 15)

        
        self.valuation_start_col=2 #This is the first data of valuation data, not the row title
        #Page Title
        self.write_to_sheet( 1, 1, "Valuation Comparables", format_name="title")
        
        # Create the color banner row
        self.quant_comps_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet( 2, col, "", format_name="color_banner")
    
        #----Valuation Comps----#
        #Write the headers
        row=4
        col=self.valuation_start_col-1
        self.write_to_sheet( row, col, "Vaulation Comparables", format_name="bold") #Write the firm name
        col+=1
        row+=1
        
        #Write the firm name headers
        '''
        TODO: Fix
        self.quant_comps_sheet.set_row(row, 30) #Set the header height to 2x normal cell height
        for key in self.business_object.comparables_valuation['EBITDA'].keys():
            #TODO: Make this reader find the first item in the dict, not assume EBITDA is in it
            self.write_to_sheet( row, col, key, format_name="bottom_border") #Write the firm name
            col+=1
        self.write_to_sheet( row, col, "Median", format_name="bottom_border") #Write the header for median
        col+=1
        self.write_to_sheet( row, col, "Average", format_name="bottom_border") #Write the header for average
        row+=1
        for attribute, attribute_dict in self.business_object.comparables_valuation.items(): 
            logging.debug(f"\nAttribute is: \n\t{attribute}\n\n Attribute Dict is\n\t {attribute_dict}\n\n")
            col=1
            self.write_to_sheet( row, col, attribute, format_name="plain") #Write the attribute
            col+=1
            
            for firm_attribute_dict in attribute_dict.values():
                self.write_to_sheet( row, col, firm_attribute_dict['value'], format_name="plain") #Write the data
                col+=1
            
            
            #Median and Average
            self.valuation_final_col=col-1
            formula_string = f"=MEDIAN({get_cell_identifier(row, self.valuation_start_col)}:{get_cell_identifier(row, self.valuation_final_col)})"
            self.write_to_sheet( row, col, formula_string, format_name="plain") #Write the median calculation
            col+=1
            formula_string = f"=AVERAGE({get_cell_identifier(row, self.valuation_start_col)}:{get_cell_identifier(row, self.valuation_final_col)})"
            self.write_to_sheet( row, col, formula_string, format_name="plain") #Write the median calculation
            row+=1
            
    '''
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 14:16:06 2024

@author: mikeg
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:18:51 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
from cellManager import CellManager
import logging

#Create a recipes and Ingredients Sheet
class ComparablesQuantPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
       
        self.workbook_manager = workbook_manager
        self.business_object = business_object
        self.cell_manager = cell_manager
        self.num_forecasted_years=workbook_manager.num_forecasted_years
        self.sheet_name = 'Valuation Comps'
        self.quant_comps_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        
        #Make the sheet
        self.populate_sheet()

    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.quant_comps_sheet, row, col, formula_string, format_name, print_formula)
        
    def populate_sheet(self):
        #Set column widths
        self.quant_comps_sheet.set_column('A:A', 5)
        self.quant_comps_sheet.set_column('B:B', 20)
        self.quant_comps_sheet.set_column('C:C', 15)
        self.quant_comps_sheet.set_column('D:D', 10)
        self.quant_comps_sheet.set_column('E:J', 15)

        
        self.valuation_start_col=2 #This is the first data of valuation data, not the row title
        #Page Title
        self.write_to_sheet( 1, 1, "Valuation Comparables", format_name="title")
        
        # Create the color banner row
        self.quant_comps_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet( 2, col, "", format_name="color_banner")
    
        #----Valuation Comps----#
        #Write the headers
        row=4
        col=self.valuation_start_col-1
        self.write_to_sheet( row, col, "Vaulation Comparables", format_name="bold") #Write the firm name
        col+=1
        row+=1
        
        #Write the firm name headers
        '''
        TODO: Fix
        self.quant_comps_sheet.set_row(row, 30) #Set the header height to 2x normal cell height
        for key in self.business_object.comparables_valuation['EBITDA'].keys():
            #TODO: Make this reader find the first item in the dict, not assume EBITDA is in it
            self.write_to_sheet( row, col, key, format_name="bottom_border") #Write the firm name
            col+=1
        self.write_to_sheet( row, col, "Median", format_name="bottom_border") #Write the header for median
        col+=1
        self.write_to_sheet( row, col, "Average", format_name="bottom_border") #Write the header for average
        row+=1
        for attribute, attribute_dict in self.business_object.comparables_valuation.items(): 
            logging.debug(f"\nAttribute is: \n\t{attribute}\n\n Attribute Dict is\n\t {attribute_dict}\n\n")
            col=1
            self.write_to_sheet( row, col, attribute, format_name="plain") #Write the attribute
            col+=1
            
            for firm_attribute_dict in attribute_dict.values():
                self.write_to_sheet( row, col, firm_attribute_dict['value'], format_name="plain") #Write the data
                col+=1
            
            
            #Median and Average
            self.valuation_final_col=col-1
            formula_string = f"=MEDIAN({get_cell_identifier(row, self.valuation_start_col)}:{get_cell_identifier(row, self.valuation_final_col)})"
            self.write_to_sheet( row, col, formula_string, format_name="plain") #Write the median calculation
            col+=1
            formula_string = f"=AVERAGE({get_cell_identifier(row, self.valuation_start_col)}:{get_cell_identifier(row, self.valuation_final_col)})"
            self.write_to_sheet( row, col, formula_string, format_name="plain") #Write the median calculation
            row+=1
            
    '''