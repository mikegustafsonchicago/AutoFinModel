# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:20:05 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from workbook_sheet_manager_code import SheetManager
from datetime import datetime

class UnitIncomePage(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
        self.business_object = business_object   
       
        #Set start columns
        self.annual_year0_start=4
        self.annual_start_col=self.annual_year0_start
        self.annual_hist_start=self.annual_year0_start #Adding in some variables for historical values, although not ready to implement
        self.gap_between_annual_and_monthly=1 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_year0_start+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        #Create the sheet
        self.sheet_name = 'Unit_IS'
        
        self.populate_sheet()


    def populate_sheet(self):
        #--------- Main ----------#
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5) 
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('D:D', 10)
        #Set all the annual model column width
        for col in range(3, 4+self.num_forecasted_years*12):
            col_letter = number_to_column_letter(col)
            self.xlsxwriter_sheet.set_column(f"{col_letter}:{col_letter}", 10)
        
        #Write the page title
        self.write_to_sheet(1, 1, 'Unit Model - Income Statement', format_name='title')
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5)
        for col in range(1,(self.num_forecasted_years+1)*12+self.gap_between_annual_and_monthly):
            self.workbook_manager.validate_and_write(self.xlsxwriter_sheet, 2, col, "", format_name="color_banner")
        
        row = 5
        col = 2
        
        ##----Headers----##
        self.populate_annual_monthly_headers(row, col)
        
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
                self.write_to_sheet(row-1, self.annual_year0_start-3, line, format_name='plain')
                for revenue_source in self.business_object.revenue_sources:
                    self.create_annual_sum_from_months_line(row)
                    self.write_to_sheet(row, self.annual_year0_start-3, revenue_source["revenue_source_name"], format_name='italic')
                    ref_row = self.cell_manager.get_cell_reference("Revenue_COGS_Build", revenue_source["revenue_source_name"], format_type='row')
                    ref_col = self.cell_manager.get_cell_reference("Revenue_COGS_Build", revenue_source["revenue_source_name"], format_type='col')
                    self.create_monthly_from_single_cell(row, ref_row, ref_col, "Revenue_COGS_Build")
                    row += 1
                
                # Write total revenue line
                self.write_to_sheet(row, self.annual_year0_start-3, "Total Revenue", format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", r] for r in range(row-len(self.business_object.revenue_sources), row)])
                self.revenue_row = row
                self.cell_manager.add_cell_reference(self.sheet_name, "Total Revenue", row=row, col=self.annual_year0_start-3)
                row += 1
                self.create_percent_change_line(row, row-1)
                row += 1
                
            elif line=="Direct Costs":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='plain')
                for cost_item in self.business_object.cost_of_sales_items:
                    self.write_to_sheet(row, self.annual_year0_start-3, cost_item["cost_item_name"], format_name='italic')
                    self.create_annual_sum_from_months_line(row)
                    ref_row = self.cell_manager.get_cell_reference("Revenue_COGS_Build", cost_item["cost_item_name"], format_type='row')
                    ref_col = self.cell_manager.get_cell_reference("Revenue_COGS_Build", cost_item["cost_item_name"], format_type='col')
                    self.create_monthly_from_single_cell(row, ref_row, ref_col, "Revenue_COGS_Build")
                    row += 1
                
                # Write total direct costs line
                self.write_to_sheet(row, self.annual_year0_start-3, "Total Direct Costs", format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", r] for r in range(row-len(self.business_object.cost_of_sales_items), row)])
                self.cogs_row = row
                self.cell_manager.add_cell_reference(self.sheet_name, "Total Direct Costs", row=row, col=self.annual_year0_start-3)
                row += 1
                self.create_percent_margin_line(row, row-1)
                
            elif line == "Gross Profit":
                self.write_to_sheet(row, self.annual_year0_start-3, line, format_name='bold')
                self.create_in_column_addition_subtraction(row, [["+", self.revenue_row], ["-", self.cogs_row]]) 
                self.gross_profit_row=row
                self.cell_manager.add_cell_reference(self.sheet_name, "Gross Profit", row=row, col=self.annual_year0_start-3)
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
                    self.write_to_sheet(row, col, 0, format_name="currency")
                self.interest_row=row
                
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
