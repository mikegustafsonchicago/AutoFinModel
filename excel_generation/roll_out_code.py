# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 10:24:18 2024

@author: mikeg
"""



from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime
from workbook_sheet_manager_code import SheetManager

class RollOutPage(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
       
        #Set start columns
        self.annual_hist_start=3
        self.annual_year0_start = self.annual_hist_start + self.num_hist_years
        self.gap_between_annual_and_monthly=1 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_year0_start+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        #Create the sheet
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
        

    def populate_sheet(self):
        #--------- Main ----------#
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5) 
        self.xlsxwriter_sheet.set_column('B:B', 15) 
        self.xlsxwriter_sheet.set_column('D:D', 10)
        #Set all the annual model column width
        start_col_letter = number_to_column_letter(self.annual_hist_start)
        end_col_letter = number_to_column_letter(self.annual_year0_start+self.num_forecasted_years)
        self.xlsxwriter_sheet.set_column(f"{start_col_letter}:{end_col_letter}", 10)
        
        #Write the page title
        self.write_to_sheet(1, 1, 'Roll Out Schedule', format_name='title')
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5)
        for col in range(1,(self.num_forecasted_years+1)*12+self.gap_between_annual_and_monthly+(self.annual_year0_start-self.annual_hist_start)):
            self.workbook_manager.validate_and_write(self.xlsxwriter_sheet, 2, col, "", format_name="color_banner")
        
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
           
            
