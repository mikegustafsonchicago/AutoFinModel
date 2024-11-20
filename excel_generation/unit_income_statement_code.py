# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:20:05 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime

class UnitIncomePage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.num_forecasted_years=self.workbook_manager.num_forecasted_years    
        self.business_object = business_object
       
        #Set start columns
        self.annual_year0_start=4
        self.annual_hist_start=self.annual_year0_start #Adding in some variables for historical values, although not ready to implement
        self.gap_between_annual_and_monthly=1 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_year0_start+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        #Create the sheet
        self.sheet_name = 'Unit_IS'
        self.IS_page = self.workbook_manager.add_sheet(self.sheet_name)
        self.populate_sheet()

    #--------Function Definitions--------#
    
    def populate_headers(self, row, col):
        self.year_row=row #Save the row number for the row that years are listed
        #Annual headers
        self.write_to_sheet(row-1, self.annual_year0_start, 'Annual Pro Forma', format_name='bold')
        self.cell_manager.add_cell_reference(self.sheet_name, "Headers", "Annual", row=row, col=col) #Remember the row/col location of the first "year x" header
        start_year_date = datetime(self.business_object.start_year, 1, 1)
        self.write_to_sheet(row, self.annual_year0_start, start_year_date, format_name='year_format')
        for col in range(self.annual_year0_start+1, self.annual_year0_start+self.num_forecasted_years):
                self.write_to_sheet(row, col, f"=edate({get_cell_identifier(row, col-1)},12)", format_name='year_format')
        
        #Monthly headers
        col=self.monthly_start_col
        self.write_to_sheet(row-1, col, 'Monthly Pro Forma', format_name='bold')
        for year in range(self.business_object.start_year, self.business_object.start_year+self.num_forecasted_years):
            for month in range(1,13):
                if year ==self.business_object.start_year and month == 1:
                    self.write_to_sheet(row, col, datetime(year,month,1), format_name='year_format')
                else:
                    self.write_to_sheet(row, col, f"=edate({get_cell_identifier(row, col-1)},1)", format_name='year_format')
                self.write_to_sheet(row+1, col, calendar.month_abbr[month], format_name='bottom_border')
                col+=1
            
    def create_annual_sum_from_months_line(self, row):
        # Row should stay constant since this only iterates across columns
        for col in range(self.annual_year0_start, self.annual_year0_start + self.num_forecasted_years):
            year_row = self.cell_manager.get_cell_reference(self.sheet_name, "Headers", "Annual", format_type="row")-1 #Minus one to correct for indexing
            year_cell = get_cell_identifier(year_row, col)
            
            # Constructing the formula string with absolute columns
            formula_string = (
                "=SUMIFS("
                f"{get_cell_identifier(row, self.monthly_start_col, absolute_row=True, absolute_col=True)}:"
                f"{get_cell_identifier(row, self.monthly_start_col + 12 * self.num_forecasted_years, absolute_row=True, absolute_col=True)}, " # Cells to sum
                
                f"{get_cell_identifier(year_row, self.monthly_start_col, absolute_row=True, absolute_col=True)}:"
                f"{get_cell_identifier(year_row, self.monthly_start_col + 12 * self.num_forecasted_years, absolute_row=True, absolute_col=True)}, " # Cells to check for the right date
                
                f'">=" & DATE(YEAR({year_cell}),1,1), ' # After January of the year above
                
                f"{get_cell_identifier(year_row, self.monthly_start_col, absolute_row=True, absolute_col=True)}:"
                f"{get_cell_identifier(year_row, self.monthly_start_col + 12 * self.num_forecasted_years, absolute_row=True, absolute_col=True)}, " # Cells to check for the right date
                
                f'"<=" & DATE(YEAR({year_cell}),12,31))' # Before January of the year above
            )
            self.write_to_sheet(row, col, formula_string, format_name="currency")

    def create_percent_change_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_year0_start-3, "% Growth", format_name="grey_italic")
        for col in range(self.annual_year0_start+1, self.annual_year0_start+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_year0_start+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                past_cell = get_cell_identifier(ref_row, col-1, absolute_row=True)
                present_cell = get_cell_identifier(ref_row, col, absolute_row=True)
                formula_string = f"=({present_cell}-{past_cell})/{past_cell}"
                
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")
                
    def create_percent_margin_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_year0_start-3, "Margin (%)", format_name="grey_italic_right")
        for col in range(self.annual_year0_start+1, self.annual_year0_start+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_year0_start+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                formula_string = f"={get_cell_identifier(row-1,col)}/{get_cell_identifier(self.revenue_row,col, absolute_row=True)}"
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")

    def create_monthly_referenced_line(self, row, ref_row, ref_col, ref_sheet_name):
        #This function writes each row. The consist of annual model and monthly models.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.monthly_start_col
        col_offset = col - ref_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                formula_string = f"='{ref_sheet_name}'!{number_to_column_letter(col-col_offset)}${ref_row}"
                self.write_to_sheet(row, col, formula_string, format_name='currency_cross')
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
                    if index==0 and component == "+":
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
        self.IS_page.set_column('B:B', 25) 
        self.IS_page.set_column('D:D', 10)
        #Set all the annual model column width
        start_col_letter = number_to_column_letter(self.annual_year0_start)
        end_col_letter = number_to_column_letter(self.annual_year0_start+self.num_forecasted_years)
        self.IS_page.set_column(f"{start_col_letter}:{end_col_letter}", 10)
        
        #Write the page title
        self.write_to_sheet(1, 1, 'Unit Model - Income Statement', format_name='title')
        
        # Create the color banner row
        self.IS_page.set_row(2, 5)
        for col in range(1,(self.num_forecasted_years+1)*12+self.gap_between_annual_and_monthly):
            self.workbook_manager.validate_and_write(self.IS_page, 2, col, "", format_name="color_banner")
        
        row = 5
        col = 2
        
        ##----Headers----##
        self.populate_headers(row, col)
        
        #Data
        statement_lines_ref = ["Revenue", 
                               "Direct Costs", 
                               "Gross Profit", 
                               "SG&A",
                               "Employee Salaries",
                               "R&D",
                               "EBITDA",
                               "Depreciation",
                               "EBIT",
                               "Interest", 
                               "Taxes",
                               "Net Income"]
        
        row +=2
        
        for line in statement_lines_ref:
            self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='plain')
            #TODO: Automate IS line matching with info fed from other sources
            if line=="Revenue":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Sales Forecast", "Revenue", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Sales Forecast", "Revenue", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Sales Forecast")
                self.revenue_row = row
                row+=1
                self.create_percent_change_line(row, row-1)
                
            elif line=="Direct Costs":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Sales Forecast", "Direct_Costs", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Sales Forecast", "Direct_Costs", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Sales Forecast")
                self.cogs_row = row
                row+=1
                self.create_percent_margin_line(row, row-1)
                
            elif line == "Gross Profit":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.revenue_row], ["-", self.cogs_row]]) 
                self.gross_profit_row=row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
                
            elif line=="SG&A":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("OPEX_CAPEX", "SGA", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("OPEX_CAPEX", "SGA", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "OPEX_CAPEX")
                self.sga_row=row
                
            elif line=="Employee Salaries":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Unit Employees", "salaries", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Unit Employees", "salaries", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Unit Employees")
                self.employee_row=row
                
            elif line == "EBITDA":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.gross_profit_row], ["-", self.sga_row], ["-", self.employee_row]]) 
                self.ebitda_row = row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
            
            elif line=="Depreciation":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("OPEX_CAPEX", "Depreciation", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("OPEX_CAPEX", "Depreciation", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "OPEX_CAPEX")
                self.depreciation_row = row
                
            elif line == "EBIT":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.ebitda_row], ["-", self.depreciation_row]]) 
                self.ebit_row = row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
                
            elif line=="Interest":
                self.create_annual_sum_from_months_line(row)
                for col in range(self.monthly_start_col, self.monthly_start_col+12*self.num_forecasted_years):
                    self.write_to_sheet(row, col, "0", format_name="currency")
                self.interest_row=row
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Sales Forecast")
                
            elif line=="Taxes":
                self.create_annual_sum_from_months_line(row)
                self.write_to_sheet(row, self.annual_year0_start-2, 0.21, format_name="percent_input")
                tax_rate_cell = get_cell_identifier(row, self.annual_year0_start-2, absolute_row=True, absolute_col=True)
                for col in range(self.monthly_start_col, self.monthly_start_col+self.num_forecasted_years*12):
                    formula_string = f'={tax_rate_cell}*{get_cell_identifier(self.ebitda_row, col)}'
                    self.write_to_sheet(row, col, formula_string, format_name='currency')
                self.tax_row=row
                
            elif line == "Net Income":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.ebit_row], ["-", self.interest_row], ["-", self.tax_row]]) 

                self.cell_manager.add_cell_reference(self.sheet_name, "Net_Income", row=row, col=self.monthly_start_col)
                row+=1
                self.create_percent_margin_line(row, row-1)
            else:
                self.write_to_sheet(row+1, self.monthly_start_col, 'hihello', format_name='bottom_border', print_formula=False)
            row+=1
            
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:20:05 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime

class UnitIncomePage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.num_forecasted_years=self.workbook_manager.num_forecasted_years    
        self.business_object = business_object
       
        #Set start columns
        self.annual_year0_start=4
        self.annual_hist_start=self.annual_year0_start #Adding in some variables for historical values, although not ready to implement
        self.gap_between_annual_and_monthly=1 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_year0_start+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        #Create the sheet
        self.sheet_name = 'Unit_IS'
        self.IS_page = self.workbook_manager.add_sheet(self.sheet_name)
        self.populate_sheet()

    #--------Function Definitions--------#
    
    def populate_headers(self, row, col):
        self.year_row=row #Save the row number for the row that years are listed
        #Annual headers
        self.write_to_sheet(row-1, self.annual_year0_start, 'Annual Pro Forma', format_name='bold')
        self.cell_manager.add_cell_reference(self.sheet_name, "Headers", "Annual", row=row, col=col) #Remember the row/col location of the first "year x" header
        start_year_date = datetime(self.business_object.start_year, 1, 1)
        self.write_to_sheet(row, self.annual_year0_start, start_year_date, format_name='year_format')
        for col in range(self.annual_year0_start+1, self.annual_year0_start+self.num_forecasted_years):
                self.write_to_sheet(row, col, f"=edate({get_cell_identifier(row, col-1)},12)", format_name='year_format')
        
        #Monthly headers
        col=self.monthly_start_col
        self.write_to_sheet(row-1, col, 'Monthly Pro Forma', format_name='bold')
        for year in range(self.business_object.start_year, self.business_object.start_year+self.num_forecasted_years):
            for month in range(1,13):
                if year ==self.business_object.start_year and month == 1:
                    self.write_to_sheet(row, col, datetime(year,month,1), format_name='year_format')
                else:
                    self.write_to_sheet(row, col, f"=edate({get_cell_identifier(row, col-1)},1)", format_name='year_format')
                self.write_to_sheet(row+1, col, calendar.month_abbr[month], format_name='bottom_border')
                col+=1
            
    def create_annual_sum_from_months_line(self, row):
        # Row should stay constant since this only iterates across columns
        for col in range(self.annual_year0_start, self.annual_year0_start + self.num_forecasted_years):
            year_row = self.cell_manager.get_cell_reference(self.sheet_name, "Headers", "Annual", format_type="row")-1 #Minus one to correct for indexing
            year_cell = get_cell_identifier(year_row, col)
            
            # Constructing the formula string with absolute columns
            formula_string = (
                "=SUMIFS("
                f"{get_cell_identifier(row, self.monthly_start_col, absolute_row=True, absolute_col=True)}:"
                f"{get_cell_identifier(row, self.monthly_start_col + 12 * self.num_forecasted_years, absolute_row=True, absolute_col=True)}, " # Cells to sum
                
                f"{get_cell_identifier(year_row, self.monthly_start_col, absolute_row=True, absolute_col=True)}:"
                f"{get_cell_identifier(year_row, self.monthly_start_col + 12 * self.num_forecasted_years, absolute_row=True, absolute_col=True)}, " # Cells to check for the right date
                
                f'">=" & DATE(YEAR({year_cell}),1,1), ' # After January of the year above
                
                f"{get_cell_identifier(year_row, self.monthly_start_col, absolute_row=True, absolute_col=True)}:"
                f"{get_cell_identifier(year_row, self.monthly_start_col + 12 * self.num_forecasted_years, absolute_row=True, absolute_col=True)}, " # Cells to check for the right date
                
                f'"<=" & DATE(YEAR({year_cell}),12,31))' # Before January of the year above
            )
            self.write_to_sheet(row, col, formula_string, format_name="currency")

    def create_percent_change_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_year0_start-3, "% Growth", format_name="grey_italic")
        for col in range(self.annual_year0_start+1, self.annual_year0_start+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_year0_start+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                past_cell = get_cell_identifier(ref_row, col-1, absolute_row=True)
                present_cell = get_cell_identifier(ref_row, col, absolute_row=True)
                formula_string = f"=({present_cell}-{past_cell})/{past_cell}"
                
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")
                
    def create_percent_margin_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_year0_start-3, "Margin (%)", format_name="grey_italic_right")
        for col in range(self.annual_year0_start+1, self.annual_year0_start+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_year0_start+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                formula_string = f"={get_cell_identifier(row-1,col)}/{get_cell_identifier(self.revenue_row,col, absolute_row=True)}"
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")

    def create_monthly_referenced_line(self, row, ref_row, ref_col, ref_sheet_name):
        #This function writes each row. The consist of annual model and monthly models.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.monthly_start_col
        col_offset = col - ref_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                formula_string = f"='{ref_sheet_name}'!{number_to_column_letter(col-col_offset)}${ref_row}"
                self.write_to_sheet(row, col, formula_string, format_name='currency_cross')
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
                    if index==0 and component == "+":
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
        self.IS_page.set_column('B:B', 25) 
        self.IS_page.set_column('D:D', 10)
        #Set all the annual model column width
        start_col_letter = number_to_column_letter(self.annual_year0_start)
        end_col_letter = number_to_column_letter(self.annual_year0_start+self.num_forecasted_years)
        self.IS_page.set_column(f"{start_col_letter}:{end_col_letter}", 10)
        
        #Write the page title
        self.write_to_sheet(1, 1, 'Unit Model - Income Statement', format_name='title')
        
        # Create the color banner row
        self.IS_page.set_row(2, 5)
        for col in range(1,(self.num_forecasted_years+1)*12+self.gap_between_annual_and_monthly):
            self.workbook_manager.validate_and_write(self.IS_page, 2, col, "", format_name="color_banner")
        
        row = 5
        col = 2
        
        ##----Headers----##
        self.populate_headers(row, col)
        
        #Data
        statement_lines_ref = ["Revenue", 
                               "Direct Costs", 
                               "Gross Profit", 
                               "SG&A",
                               "Employee Salaries",
                               "R&D",
                               "EBITDA",
                               "Depreciation",
                               "EBIT",
                               "Interest", 
                               "Taxes",
                               "Net Income"]
        
        row +=2
        
        for line in statement_lines_ref:
            self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='plain')
            #TODO: Automate IS line matching with info fed from other sources
            if line=="Revenue":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Sales Forecast", "Revenue", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Sales Forecast", "Revenue", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Sales Forecast")
                self.revenue_row = row
                row+=1
                self.create_percent_change_line(row, row-1)
                
            elif line=="Direct Costs":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Sales Forecast", "Direct_Costs", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Sales Forecast", "Direct_Costs", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Sales Forecast")
                self.cogs_row = row
                row+=1
                self.create_percent_margin_line(row, row-1)
                
            elif line == "Gross Profit":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.revenue_row], ["-", self.cogs_row]]) 
                self.gross_profit_row=row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
                
            elif line=="SG&A":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("OPEX_CAPEX", "SGA", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("OPEX_CAPEX", "SGA", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "OPEX_CAPEX")
                self.sga_row=row
                
            elif line=="Employee Salaries":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Unit Employees", "salaries", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Unit Employees", "salaries", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Unit Employees")
                self.employee_row=row
                
            elif line == "EBITDA":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.gross_profit_row], ["-", self.sga_row], ["-", self.employee_row]]) 
                self.ebitda_row = row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
            
            elif line=="Depreciation":
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("OPEX_CAPEX", "Depreciation", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("OPEX_CAPEX", "Depreciation", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "OPEX_CAPEX")
                self.depreciation_row = row
                
            elif line == "EBIT":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.ebitda_row], ["-", self.depreciation_row]]) 
                self.ebit_row = row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
                
            elif line=="Interest":
                self.create_annual_sum_from_months_line(row)
                for col in range(self.monthly_start_col, self.monthly_start_col+12*self.num_forecasted_years):
                    self.write_to_sheet(row, col, "0", format_name="currency")
                self.interest_row=row
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Sales Forecast")
                
            elif line=="Taxes":
                self.create_annual_sum_from_months_line(row)
                self.write_to_sheet(row, self.annual_year0_start-2, 0.21, format_name="percent_input")
                tax_rate_cell = get_cell_identifier(row, self.annual_year0_start-2, absolute_row=True, absolute_col=True)
                for col in range(self.monthly_start_col, self.monthly_start_col+self.num_forecasted_years*12):
                    formula_string = f'={tax_rate_cell}*{get_cell_identifier(self.ebitda_row, col)}'
                    self.write_to_sheet(row, col, formula_string, format_name='currency')
                self.tax_row=row
                
            elif line == "Net Income":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.ebit_row], ["-", self.interest_row], ["-", self.tax_row]]) 

                self.cell_manager.add_cell_reference(self.sheet_name, "Net_Income", row=row, col=self.monthly_start_col)
                row+=1
                self.create_percent_margin_line(row, row-1)
            else:
                self.write_to_sheet(row+1, self.monthly_start_col, 'hihello', format_name='bottom_border', print_formula=False)
            row+=1
            