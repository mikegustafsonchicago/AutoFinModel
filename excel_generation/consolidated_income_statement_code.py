# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 10:22:00 2024

@author: mikeg
"""


from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime
import logging
from workbook_sheet_manager_code import SheetManager

class ConsolidatedIncomeStatement(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
       
        #Set start columns
        self.annual_hist_start=4
        self.annual_start_col = self.annual_hist_start + self.num_hist_years
        self.annual_year0_start = self.annual_start_col
        self.gap_between_annual_and_monthly=1 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_year0_start+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols


        self.populate_sheet()

    #--------Function Definitions--------#
    
    def populate_headers(self, row, col):
        self.year_row=row #Save the row number for the row that years are listed
        #Annual headers
        self.write_to_sheet(row-1, self.annual_year0_start, 'Pro Forma', format_name='bold')
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
                
        #Line below the headers
        for col in range(self.annual_hist_start, self.annual_year0_start+self.num_forecasted_years):
            self.write_to_sheet(row+1, col, '', format_name='bottom_border')
        
        #Historical headers
        self.write_to_sheet(row-1, self.annual_hist_start, 'Historical', format_name='bold')
        col = self.annual_hist_start
        if self.business_object.hist_IS and "historical_financials" in self.business_object.hist_IS:
            for year_data in self.business_object.hist_IS["historical_financials"]:
                ref_year = datetime(year_data["year"], 1, 1)
                self.write_to_sheet(row, col, ref_year, format_name='year_format')
                col+=1

    
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
        self.write_to_sheet(1, 1, 'Consolidated Income Statement', format_name='title')
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5)
        for col in range(1,(self.num_forecasted_years+1)*12+self.gap_between_annual_and_monthly+(self.annual_year0_start-self.annual_hist_start)):
            self.workbook_manager.validate_and_write(self.xlsxwriter_sheet, 2, col, "", format_name="color_banner")
        
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
            #Write the row names like "Revenue", "Direct Costs", etc
            self.write_to_sheet(row, self.annual_hist_start-3, line, format_name='plain')
            
            if line=="Revenue":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'currency')
                #Annual Pro Forma
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Unit_IS", "Net_Income", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Unit_IS", "Net_Income", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Unit_IS")
                self.revenue_row = row
                #row+=1
                #self.create_percent_change_line(row, row-1)
                
            elif line=="Direct Costs":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'currency')
                #Annual Pro Forma
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Unit_IS", "Total Direct Costs", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Unit_IS", "Total Direct Costs", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Unit_IS")
                self.cogs_row = row
                #row+=1
                #self.create_percent_margin_line(row, row-1)
                
            elif line == "Gross Profit":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'sum_line')
                #Annual Pro Forma
                self.write_to_sheet(row, self.annual_hist_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.revenue_row], ["-", self.cogs_row]]) 
                self.gross_profit_row=row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
                
            elif line=="SG&A":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'currency')
                #Annual Pro Forma
                ref_row = self.cell_manager.get_cell_reference("OPEX_CAPEX", "SGA", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("OPEX_CAPEX", "SGA", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "OPEX_CAPEX")
                self.sga_row=row
                
            elif line=="Employee Salaries":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'currency')
                #Annual Pro Forma
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Unit Employees", "salaries", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Unit Employees", "salaries", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Unit Employees")
                self.employee_row=row
                
            elif line == "EBITDA":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'sum_line')
                #Annual Pro Forma
                self.write_to_sheet(row, self.annual_hist_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.gross_profit_row], ["-", self.sga_row], ["-", self.employee_row]]) 
                self.ebitda_row = row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
            
            elif line=="Depreciation":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'currency')
                #Annual Pro Forma
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("OPEX_CAPEX", "Depreciation", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("OPEX_CAPEX", "Depreciation", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "OPEX_CAPEX")
                self.depreciation_row = row
                
            elif line == "EBIT":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'sum_line')
                #Annual Pro Forma
                self.write_to_sheet(row, self.annual_hist_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.ebitda_row], ["-", self.depreciation_row]]) 
                self.ebit_row = row
                row+=1
                self.create_percent_margin_line(row, row-1)
                row+=1
                
            elif line=="Interest":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'currency')
                #Annual Pro Forma
                self.create_annual_sum_from_months_line(row)
                ref_row = self.cell_manager.get_cell_reference("Revenue COGS Build", "Total Revenue", format_type='row')
                ref_col = self.cell_manager.get_cell_reference("Revenue COGS Build", "Total Revenue", format_type='col')
                self.create_monthly_referenced_line(row, ref_row, ref_col, "Revenue COGS Build")
                self.interest_row=row
                
            elif line=="Taxes":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'currency')
                #Annual Pro Forma
                self.create_annual_sum_from_months_line(row)
                self.write_to_sheet(row, self.annual_hist_start-2, 0.21, format_name="percent_input")
                self.tax_rate_cell = get_cell_identifier(row, self.annual_hist_start-2, absolute_row=True, absolute_col=True)
                for col in range(self.monthly_start_col, self.monthly_start_col+self.num_forecasted_years*12):
                    formula_string = f'={self.tax_rate_cell}*{get_cell_identifier(self.ebitda_row, col)}'
                    self.write_to_sheet(row, col, formula_string, format_name='currency')
                self.tax_row=row
                
            elif line == "Net Income":
                #Historical
                #TODO: Fix self.populate_annual_hist_data(row, line, format_name = 'sum_line')
                #Annual Pro Forma
                self.write_to_sheet(row, self.annual_hist_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.ebit_row], ["-", self.interest_row], ["-", self.tax_row]]) 

                self.cell_manager.add_cell_reference(self.sheet_name, "Net_Income", row=row, col=self.monthly_start_col)
                row+=1
                self.create_percent_margin_line(row, row-1)
            else:
                self.write_to_sheet(row+1, self.monthly_start_col, 'hihello', format_name='bottom_border')
            row+=1
            