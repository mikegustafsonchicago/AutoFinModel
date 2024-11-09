# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 08:38:38 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime

class OpexCapexPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.sheet_name='OPEX_CAPEX'
        self.workbook_manager.cell_info[self.sheet_name]={}
        
        self.num_forecasted_years=workbook_manager.num_forecasted_years
        #Set start columns
        self.annual_year0_start=8
        self.annual_hist_start=self.annual_year0_start #Adding in some variables for historical values, although not ready to implement
        self.gap_between_annual_and_monthly=2 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_year0_start+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        self.expenses_layout_start_col=1 #The column that is the first for the details of the various expenses
        
        #Make the sheet
        self.operating_expenses_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        
        self.populate_sheet()
        
    #--------Function Definitions--------#
    
    def populate_headers(self, row, col):
        #Annual headers
        self.year_row=row
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



    def create_monthly_line_from_cell(self, row, ref_cell):
        #This function writes each row. The consist of annual model and monthly models.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.monthly_start_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                #TODO: Automate which cells this pulls from
                formula_string = f"=${ref_cell}"
                self.write_to_sheet(row, col, formula_string, format_name='currency')
                col+=1
                
    def create_total_line(self, row, start_col, num_print_cols, num_sum_rows):
        #num_print_cols is the number of columns to apply the sum formula to
        for col in range(start_col, start_col+num_print_cols):
            formula_string = (f"=sum({number_to_column_letter(col)}${row-num_sum_rows}"
                              f":{number_to_column_letter(col)}${row})")
            self.write_to_sheet(row, col, formula_string, format_name="sum_line")
    
    def create_capex_line(self, row):
        #This function writes an equation in each row that sees if it's time to make a capex purchase, given the info in the CAPEX discussion.
        #Function consists of annual model and monthly models.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.monthly_start_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                #TODO: Automate which cells this pulls from
                purchase_year_cell = get_cell_identifier(row, self.capex_date_col, absolute_col=True)
                current_year_cell = get_cell_identifier(self.year_row, col)
                current_month_cell = get_cell_identifier(self.year_row+1, col)
                depreciation_life_cell = get_cell_identifier(row, self.capex_life_col)
                purchase_cost_cell = get_cell_identifier(row, self.capex_amount_col)
                formula_string = (
                                    f'=IF(AND('
                                    f'{current_year_cell}>={purchase_year_cell}, '# AND condition 1. Ensure the forecast year is on or after the purchase year
                                    f'MOD(({purchase_year_cell}-YEAR({current_year_cell})), {depreciation_life_cell})=0, ' # AND condition 2. Check if the year difference matches the depreciation cycle (e.g., every X years)        
                                    f'{current_month_cell}="Jan"), ' #AND condition 3. Ensure the expense is applied only in January
                                    f'{purchase_cost_cell}, ' # Return the purchase cost if all conditions are true
                                    f'0)' # Return 0 if any condition is false (no expense)
                                )
                self.write_to_sheet(row, col, formula_string, format_name='currency')
                col+=1
    
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False, is_formula=False, url_display=None):
        self.workbook_manager.validate_and_write(self.operating_expenses_sheet, row, col, formula_string, format_name, print_formula, url_display)
    
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.operating_expenses_sheet.set_column('A:A', 5)  
        self.operating_expenses_sheet.set_column('B:B', 25) 
        self.operating_expenses_sheet.set_column('C:C', 10)
        self.operating_expenses_sheet.set_column('D:D', 15) 
        self.operating_expenses_sheet.set_column('E:E', 12)
        self.operating_expenses_sheet.set_column('F:F', 30)
        self.operating_expenses_sheet.set_column('G:G', 10)
        
        # -- Headers and titles -- #
        
        #Page Title
        self.write_to_sheet(1, 1, 'Operating and Capital Expenditures', format_name="title")
        
        # Create the color banner row
        self.operating_expenses_sheet.set_row(2, 5) #Make the row heighth smaller
        for col in range(1,10):
            self.write_to_sheet(2, col, "", format_name="color_banner")
        
        
        col=self.annual_year0_start
        row = 5
        
        ##----Headers----##
        self.populate_headers(row, col)
        col=self.expenses_layout_start_col
        
        #----SG&A----#
        self.write_to_sheet(row, col, "Operating Expenditures", format_name="bold")
        row+=1
        self.write_to_sheet(row, col, "Expense", format_name="underline_wrap")
        self.write_to_sheet(row, col+1, "Amount", format_name="underline_wrap")
        self.write_to_sheet(row, col+2, "Frequency", format_name="underline_wrap")
        self.write_to_sheet(row, col+4, "Notes/Assumptions", format_name="underline_wrap")
    
        row += 1  

        for expense in self.business_object.operating_expenses:
            self.write_to_sheet(row, col, expense['expense_name'])
            self.write_to_sheet(row, col + 1, expense['amount'], format_name="currency_input")
            self.write_to_sheet(row, col + 2, expense['frequency'], format_name="input")
            self.write_to_sheet(row, col + 4, expense['notes'])
            self.write_to_sheet(row, col + 5, " ") #Need to fill in adjacent cell so the notes text doesn't run on
            self.create_monthly_line_from_cell(row, get_cell_identifier(row, col + 1))
            self.create_annual_sum_from_months_line(row)
            row += 1
        
        #Sum the CAPEX info and save the cell location
        self.create_total_line(row, self.annual_year0_start, self.num_forecasted_years, len(self.business_object.operating_expenses))
        self.create_total_line(row, self.monthly_start_col, 12*self.num_forecasted_years, len(self.business_object.operating_expenses))
        self.cell_manager.add_cell_reference(self.sheet_name, "SGA", row=row, col=self.monthly_start_col)#Save the cell location
        
        row+=2
        
        
        #----Capital Expenses----#
        self.write_to_sheet(row, col, "Capital Expenditures", format_name="bold")
        row+=1
        #Write the labels
        self.write_to_sheet(row, col, "Expense", format_name="underline_wrap")
        self.write_to_sheet(row, col+1, "Amount", format_name="underline_wrap")
        self.capex_amount_col = col+1 #Store the purchase year location info
        self.write_to_sheet(row, col+2, "Depreciation Life", format_name="underline_wrap")
        self.capex_life_col = col+2 #Store the purchase year location info
        self.write_to_sheet(row, col+3, "Purchase Date", format_name="underline_wrap")
        self.capex_date_col = col+3 #Store the purchase year location info
        self.write_to_sheet(row, col+4, "Notes/Assumptions", format_name="underline_wrap")
    
        row += 1  

        for item in self.business_object.capex_items:
            self.write_to_sheet(row, col, item['expense_name'])
            self.write_to_sheet(row, col + 1, item['amount'], format_name="currency_input")
            self.write_to_sheet(row, col + 2, item['depreciation_life'], format_name="input")
            self.write_to_sheet(row, col + 3, datetime(item['purchase_year'], 1, 1), format_name="date_input_YYYY")
            self.write_to_sheet(row, col + 4, item.get('notes', ''))
            self.write_to_sheet(row, col + 5, " ") #Need to fill in adjacent cell so the notes text doesn't run on
            self.create_capex_line(row)
            self.create_annual_sum_from_months_line(row)
            row += 1
        
        #Sum the CAPEX info and save the cell location
        self.create_total_line(row, self.annual_year0_start, self.num_forecasted_years, len(self.business_object.capex_items))
        self.create_total_line(row, self.monthly_start_col, 12*self.num_forecasted_years, len(self.business_object.capex_items))
        self.cell_manager.add_cell_reference(self.sheet_name, "CAPEX", row=row, col=self.monthly_start_col)#Save the cell location
        
        row+=2
        
        #----Depreciation (Created with CAPEX numbers)----#
        self.write_to_sheet(row, col, "Depreciation Calculations", format_name="bold")
        row+=1
        self.write_to_sheet(row, col, "Expense", format_name="underline_wrap")
        self.write_to_sheet(row, col+1, "Amount", format_name="underline_wrap")
        self.write_to_sheet(row, col+2, "Depreciation Life", format_name="underline_wrap")
        self.write_to_sheet(row, col+3, "Monthly Depreciation", format_name="underline_wrap")
    
        row += 1  

        for item in self.business_object.capex_items:
            self.write_to_sheet(row, col, item['expense_name'])
            self.write_to_sheet(row, col + 1, item['amount'], format_name="currency_input")
            self.write_to_sheet(row, col + 2, item['depreciation_life'], format_name="input")
            formula_string = f"={get_cell_identifier(row, col+1)}/({get_cell_identifier(row, col+2)}*12)"
            self.write_to_sheet(row, col + 3, formula_string, format_name="currency")
            self.create_capex_line(row)
            self.create_annual_sum_from_months_line(row)
            
            self.create_monthly_line_from_cell(row, get_cell_identifier(row, col+3))
            row += 1
            
            #Sum the CAPEX info and save the cell location
            self.create_total_line(row, self.annual_year0_start, self.num_forecasted_years, len(self.business_object.capex_items))
            self.create_total_line(row, self.monthly_start_col, 12*self.num_forecasted_years, len(self.business_object.capex_items))
            self.cell_manager.add_cell_reference(self.sheet_name, "Depreciation", row=row, col=self.monthly_start_col)#Save the cell location

        
        #----Sources----#
        row+=3
        self.write_to_sheet(row, col, "Sources", format_name="bold")
        row+=1
        for item in self.business_object.operating_expenses: 
            self.write_to_sheet(row, col, item['expense_name'], format_name='small_italic')
            self.write_to_sheet(row, col+1, item['source_link'], format_name="URL_small", url_display=item['source_string'])
            self.operating_expenses_sheet.set_row(row, 10) #Make the row heighth smaller
            row+=1
        for item in self.business_object.capex_items: 
            self.write_to_sheet(row, col, item['expense_name'], format_name='small_italic')
            self.write_to_sheet(row, col+1, item['source_link'], format_name="URL_small", url_display=item['source_string'])
            self.operating_expenses_sheet.set_row(row, 10) #Make the row heighth smaller
            row+=1