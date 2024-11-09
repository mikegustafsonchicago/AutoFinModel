# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 13:06:07 2024

@author: mikeg
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 08:38:38 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier
import calendar

class EmployeePage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.sheet_name='Unit Employees'
        self.workbook_manager.cell_info[self.sheet_name]={}
        
        self.num_forecasted_years=workbook_manager.num_forecasted_years
        #Set start columns
        self.annual_start_col=10
        self.gap_between_annual_and_monthly=2 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_start_col+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        
        #Make the sheet
        self.employees_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        
        self.populate_sheet()
        
    #--------Function Definitions--------#
    def create_annual_sum_from_months_line(self, row):
        #Row should stay constant since this only iterates across columns
        #start_col is the column index of the first column printed
        #ref_row and ref_col are the indicies of the reference cell that's being transposed here
        for col in range(self.annual_start_col, self.annual_start_col+self.num_forecasted_years):
            if_row = self.cell_manager.get_cell_reference(self.sheet_name, "Headers", "Annual", format_type="row")
            monthly_start_col_letter = number_to_column_letter(self.monthly_start_col) #Get the letter index of the first column in the monthly model
            monthly_end_col_letter = number_to_column_letter(self.monthly_start_col+(12*self.num_forecasted_years)) #Get the letter index of the last column in the monthly model
            formula_string = (f"=sumif(${monthly_start_col_letter}{if_row}:${monthly_end_col_letter}{if_row}, "
                              f"{number_to_column_letter(col)}{if_row}, "
                              f"${monthly_start_col_letter}{row+1}:${monthly_end_col_letter}{row+1})"
                            ) #xlsxwriter indexes from 0, excel doesn't.
            self.write_to_sheet(row, col, formula_string, format_name="currency", print_formula=False)



    def create_monthly_line(self, row, ref_cell, ref_sheet_name):
        #This function writes each row. The consist of annual model and monthly models.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.monthly_start_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                #TODO: Automate which cells this pulls from
                formula_string = f"=${ref_cell}"
                self.write_to_sheet(row, col, formula_string, format_name='currency', print_formula=False)
                col+=1
                
    def create_total_line(self, row, start_col, num_print_cols, num_sum_rows):
        #num_print_cols is the number of columns to apply the sum formula to
        for col in range(start_col, start_col+num_print_cols):
            formula_string = (f"=sum({number_to_column_letter(col)}${row-num_sum_rows}"
                              f":{number_to_column_letter(col)}${row})")
            self.write_to_sheet(row, col, formula_string, format_name="sum_line")
    
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False, is_formula=False, url_display=None):
        self.workbook_manager.validate_and_write(self.employees_sheet, row, col, formula_string, format_name, print_formula, url_display)
    
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.employees_sheet.set_column('A:A', 5)  
        self.employees_sheet.set_column('B:B', 25) 
        self.employees_sheet.set_column('C:C', 10)
        self.employees_sheet.set_column('D:D', 10) 
        self.employees_sheet.set_column('E:E', 10)
        self.employees_sheet.set_column('F:F', 10)
        self.employees_sheet.set_column('G:G', 10)
        self.employees_sheet.set_column('H:H', 30)
        
        # -- Headers and titles -- #
        
        #Page Title
        self.write_to_sheet(1, 1, 'Unit Employees', format_name="title")
        
        # Create the color banner row
        self.employees_sheet.set_row(2, 5) #Make the row heighth smaller
        for col in range(1,10):
            self.write_to_sheet(2, col, "", format_name="color_banner")
        
        
        col=self.annual_start_col
        row = 5
        
        ##----Model Titles----##
        self.write_to_sheet(row, self.annual_start_col, "Annual Model", format_name="bold")
        self.write_to_sheet(row, self.monthly_start_col, 'Monthly Model', format_name="bold")
        #Make the annual roll up
        
        row+=1
        self.cell_manager.add_cell_reference(self.sheet_name, "Headers", "Annual", row=row, col=self.annual_start_col) #Remember the row/col location of the first "year x" header for the annual model
        self.cell_manager.add_cell_reference(self.sheet_name, "Headers", "Monthly", row=row, col=self.annual_start_col) #Remember the row/col location of the first "year x" header for the monthly model
        #Years/Months Labels
        for year in range(1, self.num_forecasted_years+1):
            #Annual Model
            self.write_to_sheet(row, self.annual_start_col+year-1, "Year "+str(year), format_name="plain")
            self.write_to_sheet(row+1, self.annual_start_col+year-1, '', format_name="bottom_border")
        col=self.monthly_start_col
        
        #Monthly Model
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                self.write_to_sheet(row, col, "Year "+str(year), format_name="plain")
                self.write_to_sheet(row+1, col, calendar.month_abbr[month], format_name="bottom_border")
                col+=1
       
                
       #--- Fill in the data---#
        row=7
        col=1
        self.write_to_sheet(row, col, "Role", format_name="underline_wrap")
        self.write_to_sheet(row, col+1, "Number", format_name="underline_wrap")
        self.write_to_sheet(row, col+2, "Wage", format_name="underline_wrap")
        self.write_to_sheet(row, col+3, "Wage Type", format_name="underline_wrap")
        self.write_to_sheet(row, col+4, "Monthly Hours", format_name="underline_wrap")
        self.write_to_sheet(row, col+5, "Monthly Wage", format_name="underline_wrap")
        self.write_to_sheet(row, col+6, "Notes", format_name="underline_wrap")
        row+=1
        
        for employee in self.business_object.employees:
            self.write_to_sheet(row, col, employee["role"])
            self.write_to_sheet(row, col + 1, employee["number"], format_name="input")
            if employee["wage_type"]=="salary":
                self.write_to_sheet(row, col + 2, employee["wage"], format_name="currency_input") #Don't write in cents for a salaried employees amount. Too many digits
            else:
                self.write_to_sheet(row, col + 2, employee["wage"], format_name="currency_input_cents")
            self.write_to_sheet(row, col + 3, employee["wage_type"], format_name="input")
            self.write_to_sheet(row, col + 4, employee["monthly_hours"], format_name="input")
            wage_amount_cell = get_cell_identifier(row, col+2)
            wage_type_cell = get_cell_identifier(row, col+3)
            monthly_hours_cell = get_cell_identifier(row, col+4)
            formula_string = f'=if({wage_type_cell}="salary",{wage_amount_cell}/12, {monthly_hours_cell}*{wage_amount_cell})'
            self.write_to_sheet(row, col + 5, formula_string, format_name='currency')
            self.write_to_sheet(row, col + 6, employee["notes"])
            self.write_to_sheet(row, col + 7, " ")#Prevents notes text from running into more cells
            
            self.create_monthly_line(row, get_cell_identifier(row, col+5), self.employees_sheet)
            self.create_annual_sum_from_months_line(row)
            row += 1
            
        #Sum the CAPEX info and save the cell location
        self.create_total_line(row, self.annual_start_col, self.num_forecasted_years, len(self.business_object.employees))
        self.create_total_line(row, self.monthly_start_col, 12*self.num_forecasted_years, len(self.business_object.employees))
        self.cell_manager.add_cell_reference(self.sheet_name, "salaries", row=row, col=self.monthly_start_col)#Save the cell location

        #----Sources----#
        row+=3
        self.write_to_sheet(row, col, "Sources", format_name="bold")
        row+=1
        for item in self.business_object.employees: 
            self.write_to_sheet(row, col, item['role'], format_name='small_italic')
            self.write_to_sheet(row, col+1, item['source_link'], format_name="URL_small", url_display=item['source_string'])
            self.employees_sheet.set_row(row, 10) #Make the row heighth smaller
            row+=1