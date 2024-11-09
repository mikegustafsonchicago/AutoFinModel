# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 10:25:52 2024

@author: mikeg
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 11:43:02 2024

@author: mikeg
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:20:05 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
import calendar

class ConsolidatedCashFlowsPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.num_forecasted_years=self.workbook_manager.num_forecasted_years    
       
        #Set start columns
        self.annual_start_col=4
        self.gap_between_annual_and_monthly=1 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_start_col+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        #Create the sheet
        self.sheet_name = 'Consolidated_CF'
        self.CF_page = self.workbook_manager.add_sheet(self.sheet_name)
        self.populate_sheet()

    #--------Function Definitions--------#
    def create_annual_sum_from_months_line(self, row):
        #Row should stay constant since this only iterates across columns
        for col in range(self.annual_start_col, self.annual_start_col+self.num_forecasted_years):
            if_row = self.cell_manager.get_cell_reference(self.sheet_name, "Headers", "Annual", format_type="row")
            
            formula_string = (f"=sumif($O{if_row}:$ZZ{if_row}, {number_to_column_letter(col)}{if_row}, "
                              f"$O{row+1}:$ZZ{row+1})"
                            ) #xlsxwriter indexes from 0, excel doesn't.
            self.write_to_sheet(row, col, formula_string, format_name="currency", print_formula=False)

    def create_percent_change_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_start_col-3, "% Growth", format_name="grey_italic")
        for col in range(self.annual_start_col+1, self.annual_start_col+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_start_col+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                past_cell = get_cell_identifier(ref_row, col-1, absolute_row=True)
                present_cell = get_cell_identifier(ref_row, col, absolute_row=True)
                formula_string = f"=({present_cell}-{past_cell})/{past_cell}"
                
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")

    def create_monthly_referenced_line(self, row, ref_row, ref_col, ref_sheet_name):
        #This function writes each row. The consist of annual model and monthly models.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.monthly_start_col
        col_offset = col - ref_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                #TODO: Automate which cells this pulls from
                formula_string = f"='{ref_sheet_name}'!{number_to_column_letter(col-col_offset)}${ref_row}"
                self.write_to_sheet(row, col, formula_string, format_name='currency_cross', print_formula=False)
                col+=1
                
    def create_total_line(self, row, start_col, num_print_cols, num_sum_rows):
        #num_print_cols is the number of columns to apply the sum formula to
        for col in range(start_col, start_col+num_print_cols):
            formula_string = (f"=sum({number_to_column_letter(col)}${row-num_sum_rows}"
                              f":{number_to_column_letter(col)}${row})")
            self.write_to_sheet(row, col, formula_string, format_name="sum_line", print_formula=False)
    
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.CF_page, row, col, formula_string, format_name, print_formula)
    
    def populate_sheet(self):
        #--------- Main ----------#
        #Set column widths
        self.CF_page.set_column('A:A', 5) 
        self.CF_page.set_column('B:B', 25) 
        self.CF_page.set_column('D:D', 10)
        #Set all the annual model column width
        start_col_letter = number_to_column_letter(self.annual_start_col)
        end_col_letter = number_to_column_letter(self.annual_start_col+self.num_forecasted_years)
        self.CF_page.set_column(f"{start_col_letter}:{end_col_letter}", 10)
        
        #Write the page title
        self.write_to_sheet(1, 1, 'Unit Model - Statement of Cash Flows', format_name='title')
        
        # Create the color banner row
        self.CF_page.set_row(2, 5)
        for col in range(1,(self.num_forecasted_years+1)*12+self.gap_between_annual_and_monthly):
            self.workbook_manager.validate_and_write(self.CF_page, 2, col, "", format_name="color_banner")
        
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
                
                
          
            