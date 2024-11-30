# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 10:25:52 2024

@author: mikeg
"""


from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from workbook_sheet_manager_code import SheetManager

class ConsolidatedCashFlowsPage(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
       
        #Set start columns
        self.annual_start_col=4
        self.gap_between_annual_and_monthly=1 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_start_col+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        self.populate_sheet()

    #--------Function Definitions--------#


    #--------- Main ----------#
    def populate_sheet(self):
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5) 
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('D:D', 10)
        #Set all the annual model column width
        start_col_letter = number_to_column_letter(self.annual_start_col)
        end_col_letter = number_to_column_letter(self.annual_start_col+self.num_forecasted_years)
        self.xlsxwriter_sheet.set_column(f"{start_col_letter}:{end_col_letter}", 10)
        
        #Write the page title
        self.write_to_sheet(1, 1, 'Unit Model - Statement of Cash Flows', format_name='title')
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5)
        for col in range(1,(self.num_forecasted_years+1)*12+self.gap_between_annual_and_monthly):
            self.workbook_manager.validate_and_write(self.xlsxwriter_sheet, 2, col, "", format_name="color_banner")
        
        row = 5
        col = 2
        
        #Annual headers
        self.write_to_sheet(row-1, self.annual_start_col, 'Annual Model', format_name='bold')
        self.cell_manager.add_cell_reference(self.sheet_name, "Headers", "Annual", row=row, col=col) #Remember the row/col location of the first "year x" header
        for year in range(1, self.num_forecasted_years+1):
                self.write_to_sheet(row, self.annual_start_col+year-1, "Year "+str(year), format_name='plain')
                self.write_to_sheet(row+1, self.annual_start_col+year-1, '', format_name='bottom_border')
        
        #Monthly headers
        col=self.monthly_start_col
        self.write_to_sheet(row-1, col, 'Monthly Model', format_name='bold')
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                self.write_to_sheet(row, col, 'Year '+str(year), format_name='plain')
                self.write_to_sheet(row+1, col, calendar.month_abbr[month], format_name='bottom_border')
                col+=1
        
        #Data
        statement_lines_ref = ["Net Income",  "Depreciation", 
                               "Capital Expenditures", 
                               "Change in Working Capital", 
                               "Unit Cash Flow", 
                               "Accounts Recieavable", 
                               "Inventory", 
                               "Accounts Payable",
                               "NWC_Change",
                               "Fixed Assets"]
                               
        
        row +=2
        
        for line in statement_lines_ref:
            self.write_to_sheet(row, self.annual_start_col-3, line, format_name='plain')
            if line=="Net Income":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Consolidated_IS", "Net_Income", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Consolidated_IS", "Net_Income", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Consolidated_IS")
                
            elif line=="Capital Expenditures":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("OPEX_CAPEX", "CAPEX", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("OPEX_CAPEX", "CAPEX", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "OPEX_CAPEX")
            
            elif line=="Depreciation":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("OPEX_CAPEX", "Depreciation", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("OPEX_CAPEX", "Depreciation", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "OPEX_CAPEX")
                
            row+=1
                