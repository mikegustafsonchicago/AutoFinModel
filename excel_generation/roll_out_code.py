# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 10:24:18 2024

@author: mikeg
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 10:22:00 2024

@author: mikeg
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:20:05 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime

class RollOutPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.num_forecasted_years=self.workbook_manager.num_forecasted_years
        self.num_hist_years = len(self.business_object.financials)
       
        #Set start columns
        self.annual_hist_start=3
        self.annual_year0_start = self.annual_hist_start + self.num_hist_years
        self.gap_between_annual_and_monthly=1 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_year0_start+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        #Create the sheet
        self.sheet_name = 'Roll Out'
        self.IS_page = self.workbook_manager.add_sheet(self.sheet_name)
        self.populate_sheet()

    #--------Function Definitions--------#
    
    def populate_headers(self, row, col):
        self.year_row=row #Save the row number for the row that years are listed
        #Annual headers
        self.write_to_sheet(row-1, self.annual_year0_start, 'Projected', format_name='bold')
        self.cell_manager.add_cell_reference(self.sheet_name, "Headers", "Annual", row=row, col=col) #Remember the row/col location of the first "year x" header
        start_year_date = datetime(self.business_object.start_year, 1, 1)
        self.write_to_sheet(row, self.annual_year0_start, start_year_date, format_name='year_format')
        for col in range(self.annual_year0_start+1, self.annual_year0_start+self.num_forecasted_years):
                self.write_to_sheet(row, col, f"=edate({get_cell_identifier(row, col-1)},12)", format_name='year_format')
        

    def create_percent_change_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_hist_start-3, "% Growth", format_name="grey_italic_right")
        for col in range(self.annual_year0_start+1, self.annual_year0_start+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_year0_start+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                past_cell = get_cell_identifier(ref_row, col-1, absolute_row=True)
                present_cell = get_cell_identifier(ref_row, col, absolute_row=True)
                formula_string = f"=({present_cell}-{past_cell})/{past_cell}"
                
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")
                
    def create_percent_margin_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_hist_start-3, "Margin (%)", format_name="grey_italic_right")
        for col in range(self.annual_year0_start+1, self.annual_year0_start+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_year0_start+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                formula_string = f"={get_cell_identifier(row-1,col)}/{get_cell_identifier(self.revenue_row,col, absolute_row=True)}"
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")

    def create_annual_referenced_line(self, row, ref_row, ref_col, ref_sheet_name):
        #This function writes each row. The consist of annual model and monthly models.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.annual_year0_start
        col_offset = col - ref_col
        for year in range(1, self.num_forecasted_years+1):
            formula_string = f"='{ref_sheet_name}'!{number_to_column_letter(col-col_offset)}${ref_row}"
            self.write_to_sheet(row, col, formula_string, format_name='currency_cross', print_formula=False)
            col+=1
            
                
    def create_in_column_addition_subtraction(self, row, component_list, add_annual=True):
        #The component list is a list of 2 items. The first one should always either be "+" or "-". The second one is the row being added or subtracted
        if add_annual:
            range_start=self.annual_year0_start
        else:
            range_start=self.monthly_start_col
        for col in range(range_start, self.monthly_start_col+12*self.num_forecasted_years):
            if col < self.annual_year0_start+self.num_forecasted_years or col > self.monthly_start_col-1:
                formula_string="="
                for index, component in enumerate(component_list):
                    if index==0 and component[0] == "+":
                        #Don't start equations with "+"
                        formula_string += get_cell_identifier(component[1], col, absolute_row=True)
                    else:
                        formula_string += component[0] + get_cell_identifier(component[1], col, absolute_row=True)
                self.write_to_sheet(row, col, formula_string, format_name="sum_line", print_formula=False)
            
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.IS_page, row, col, formula_string, format_name, print_formula)
    
    def populate_sheet(self):
        #--------- Main ----------#
        #Set column widths
        self.IS_page.set_column('A:A', 5) 
        self.IS_page.set_column('B:B', 15) 
        self.IS_page.set_column('D:D', 10)
        #Set all the annual model column width
        start_col_letter = number_to_column_letter(self.annual_hist_start)
        end_col_letter = number_to_column_letter(self.annual_year0_start+self.num_forecasted_years)
        self.IS_page.set_column(f"{start_col_letter}:{end_col_letter}", 10)
        
        #Write the page title
        self.write_to_sheet(1, 1, 'Roll Out Schedule', format_name='title')
        
        # Create the color banner row
        self.IS_page.set_row(2, 5)
        for col in range(1,(self.num_forecasted_years+1)*12+self.gap_between_annual_and_monthly+(self.annual_year0_start-self.annual_hist_start)):
            self.workbook_manager.validate_and_write(self.IS_page, 2, col, "", format_name="color_banner")
        
        row = 5
        col = 1
        
        ##----Headers----##
        self.populate_headers(row, col)
        
        
        
        #Data
        statement_lines_ref = {
                               "Revenue": {"sheet": "Unit_IS", "ref_name":"Net_Income"}, 
                               "Direct Costs": {"sheet": "Unit_IS", "ref_name":"Net_Income"}, 
                               "Gross Profit": {"sheet": "Unit_IS", "ref_name":"Net_Income"}, 
                               "SG&A": {"sheet": "Unit_IS", "ref_name":"Net_Income"},
                               "Employee Salaries": {"sheet": "Unit_IS", "ref_name":"Net_Income"},
                               "R&D": {"sheet": "Unit_IS", "ref_name":"Net_Income"},
                               "EBITDA": {"sheet": "Unit_IS", "ref_name":"Net_Income"},
                               "Depreciation": {"sheet": "Unit_IS", "ref_name":"Net_Income"},
                               "EBIT": {"sheet": "Unit_IS", "ref_name":"Net_Income"},
                               "Interest": {"sheet": "Unit_IS", "ref_name":"Net_Income"}, 
                               "Net Income": {"sheet": "Unit_IS", "ref_name":"Net_Income"}
                               }

        
        row +=2
        
        
        #Create the roll out schedule
        self.write_to_sheet(row, col, 'Schedule of New Units', format_name='bold')
        row +=1
        self.write_to_sheet(row, col, 'Year', format_name='underline')
        self.write_to_sheet(row, col+1, 'New Units', format_name='underline')
        self.new_units_col = col+1
        self.new_units_row = row+1 #Row number of the inputs group start
        for year in range(self.business_object.start_year, self.business_object.start_year + self.num_forecasted_years):
            row+=1
            self.write_to_sheet(row, col, year)
            self.write_to_sheet(row, col+1, 0, format_name='input')
        row+=2
        
        #Create the sections that calculate the financial info based on the schedule
        for line in statement_lines_ref.keys():
            #Write the row names like "Revenue", "Direct Costs", etc
            self.write_to_sheet(row, self.annual_hist_start-2, line, format_name='bold')
            sheet_name = statement_lines_ref[line]['sheet']
            ref_name = statement_lines_ref[line]['ref_name']
            ref_row = self.cell_manager.get_cell_reference(sheet_name, ref_name, format_type='row')
            ref_col = self.cell_manager.get_cell_reference(sheet_name, ref_name, format_type='col')
            self.create_annual_referenced_line(row, ref_row, ref_col, "Unit_IS")
            line_result_row = row
            row+=2
            for year_rowwise in range(self.business_object.start_year, self.business_object.start_year + self.num_forecasted_years):
                year_delta = year_rowwise -self.business_object.start_year
                col=self.annual_year0_start
                for year_columnwise in range(self.business_object.start_year, self.business_object.start_year + self.num_forecasted_years):
                    if year_columnwise >= year_rowwise:
                        formula_string = f"=H12*{get_cell_identifier(row, self.new_units_col)}"
                        self.write_to_sheet(row, col, formula_string)
                    col+=1
                
                self.write_to_sheet(row, self.new_units_col-1, year_rowwise)
                formula_string = f"={get_cell_identifier(self.new_units_row  + year_delta, self.new_units_col, absolute_col=True)}"
                self.write_to_sheet(row, self.new_units_col, formula_string)

                row+=1
           
            