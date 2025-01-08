# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 14:16:06 2024

@author: mikeg
"""



from helper_functions import number_to_column_letter, get_cell_identifier
from cellManager import CellManager
import logging
from workbook_sheet_manager_code import SheetManager
#Create a recipes and Ingredients Sheet
class ComparablesQuantPage(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
        
        #Make the sheet
        self.populate_sheet()
        
    def populate_sheet(self):
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5)
        self.xlsxwriter_sheet.set_column('B:B', 20)
        self.xlsxwriter_sheet.set_column('C:C', 25)
        self.xlsxwriter_sheet.set_column('D:D', 25)
        self.xlsxwriter_sheet.set_column('E:E', 25)
        self.xlsxwriter_sheet.set_column('F:F', 15)
        self.xlsxwriter_sheet.set_column('G:G', 15)
        self.xlsxwriter_sheet.set_column('H:H', 15)
        self.xlsxwriter_sheet.set_column('I:I', 35)
        
        self.valuation_start_col=1 #This is the first data of valuation data, not the row title
        #Page Title
        self.write_to_sheet( 1, 1, "Valuation Comparables", format_name="title")
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet( 2, col, "", format_name="color_banner")
    
        #----Valuation Comps----#
        #Write the headers
        row=3
        col=self.valuation_start_col
        row+=1
        
        # Write column headers based on comparable_companies_structure.json
        headers = [
            "Company Name",
            "Enterprise Value ($M)", 
            "Market Cap ($M)",
            "EBITDA ($M)",
            "Equity Beta",
            "Asset Beta", 
            "EV/EBITDA",
            "Source",
            "Source Date"
        ]
        
        # Write headers
        for col_offset, header in enumerate(headers):
            self.write_to_sheet(row, col + col_offset, header, format_name="bold")
            
        row += 1
        
        
        # Get comparables data from business object
        if self.business_object.comparables_valuation:
            # Write each comparable company's data
            start_row = row
            for comp in self.business_object.comparables_valuation:
                logging.debug(f"Comparable Company: {comp}")
                self.write_to_sheet(row, col, comp["company_name"])
                self.write_to_sheet(row, col + 1, comp["enterprise_value"], format_name="number")
                self.write_to_sheet(row, col + 2, comp["market_cap"], format_name="number")
                self.write_to_sheet(row, col + 3, comp["ebitda"], format_name="number")
                self.write_to_sheet(row, col + 4, comp["equity_beta"], format_name="number")
                self.write_to_sheet(row, col + 5, comp["asset_beta"], format_name="number")
                self.write_to_sheet(row, col + 6, comp["ev_ebitda_multiple"], format_name="number")
                
                # Handle source fields with new structure
                metrics_source = comp.get("metrics_source", "-No Source-")
                metrics_notes = comp.get("metrics_notes", "")
                
                # Write source information
                if isinstance(metrics_source, dict):
                    source_display = metrics_source.get("display_value", "-No Source-")
                    source_url = metrics_source.get("url", "-No Source-")
                    self.write_to_sheet(
                        row, col + 7, 
                        f'=HYPERLINK("{source_url}", "{source_display}")', 
                        format_name="URL"
                    )
                else:
                    self.write_to_sheet(row, col + 7, metrics_source)
                
                # Write notes in the last column
                self.write_to_sheet(row, col + 8, metrics_notes)
                
                row += 1
            
            # Add median row
            self.write_to_sheet(row, col, "Median", format_name="bold")
            for col in range(2, 8):  # Columns C through H
                cell_range = f"{get_cell_identifier(row-len(self.business_object.comparables_valuation), col)}:{get_cell_identifier(row-1, col)}"
                formula = f"=MEDIAN({cell_range})"
                self.write_to_sheet(row, col, formula, format_name="sum_line")
            row += 1

            # Add average row  
            self.write_to_sheet(row, 1, "Average", format_name="plain")
            for col in range(2, 8):  # Columns C through H
                cell_range = f"{get_cell_identifier(row-len(self.business_object.comparables_valuation), col)}:{get_cell_identifier(row-1, col)}"
                formula = f"=AVERAGE({cell_range})"
                self.write_to_sheet(row, col, formula, format_name="number")
            row += 1
