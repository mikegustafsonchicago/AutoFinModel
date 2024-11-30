# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 13:06:07 2024

@author: mikeg
"""



from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from workbook_sheet_manager_code import SheetManager

class EmployeePage(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
        
        #Set start columns
        self.annual_start_col=10
        self.gap_between_annual_and_monthly=2 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_start_col+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        
        self.populate_sheet()
        
    #--------Page-Specific Function Definitions--------#
    
    
    #--------Main Function--------#
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5)  
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('C:C', 10)
        self.xlsxwriter_sheet.set_column('D:D', 10) 
        self.xlsxwriter_sheet.set_column('E:E', 10)
        self.xlsxwriter_sheet.set_column('F:F', 10)
        self.xlsxwriter_sheet.set_column('G:G', 10)
        self.xlsxwriter_sheet.set_column('H:H', 30)
        self.xlsxwriter_sheet.set_column('I:I', 8)
        self.xlsxwriter_sheet.set_column('J:J', 8)
        self.xlsxwriter_sheet.set_column('K:EL', 12)
        # -- Headers and titles -- #
        
        #Page Title
        self.write_to_sheet(1, 1, 'Unit Employees', format_name="title")
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5) #Make the row heighth smaller
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
            
            self.create_monthly_same_sheet_line(row, get_cell_identifier(row, col+5), self.xlsxwriter_sheet)
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
            self.write_to_sheet(row, col+1, item['source_link'], format_name="URL_small")
            self.xlsxwriter_sheet.set_row(row, 10) #Make the row heighth smaller
            row+=1