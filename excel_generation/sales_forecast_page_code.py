# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:05:03 2024

@author: mikeg
"""

import calendar

from helper_functions import number_to_column_letter, get_cell_identifier

class SalesForecastPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.num_forecasted_years=workbook_manager.num_forecasted_years
        
        #Create the sheet
        self.sheet_name='Sales Forecast'
        self.workbook_manager.cell_info[self.sheet_name]={}
        self.sales_forecast_sheet = workbook_manager.add_sheet(self.sheet_name)#Make the sheet
        
        #Set start columns
        self.annual_start_col=2
        self.gap_between_annual_and_monthly=2 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_start_col+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        
        self.populate_sheet()
        
    #-----------Function Definitions------------#
    def create_annual_sum_from_months_line(self, row, recipe, recipie_feature):
        #Annual forecast
        col=self.annual_start_col
        self.sales_forecast_sheet.write(row, col-1, recipe['name'])
        for col in range(2, 2+self.num_forecasted_years):
            formula_string = (f"=sumif($O6:$ZZ6, {number_to_column_letter(col)}6, "
                              f"$O{row + 1}:$ZZ{row + 1})"
                            ) #xlsxwriter indexes from 0, excel doesn't.
            self.workbook_manager.validate_and_write(self.sales_forecast_sheet, row, col, formula_string, format_name="currency")
            col+=1
            
    def create_monthly_forecast(self, row, recipe, recipie_feature):
        #Make the monthly forecast
        col=self.monthly_start_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                price_reference = self.cell_manager.get_cell_reference("Recipes", recipe['name'], recipie_feature, format_type='cell_ref', absolute_row=True)
                fraction_reference = self.cell_manager.get_cell_reference("Recipes", recipe['name'], "customer_fraction", format_type='cell_ref', absolute_row=True, absolute_col=True)
                customer_flow_reference=self.cell_manager.get_cell_reference("Customer Flow", 'monthly_visits',  format_type='cell_ref', absolute_row=True, absolute_col=True)
                formula_string = f"='Customer Flow'!{customer_flow_reference}*'recipes'!{price_reference}*'recipes'!{fraction_reference}"
                self.workbook_manager.validate_and_write(self.sales_forecast_sheet, row, col, formula_string, format_name="currency_cross") #Write the data
                col+=1
                
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.sales_forecast_sheet, row, col, formula_string, format_name, print_formula)
        
    def create_total_line(self, row, start_col, num_print_cols, num_sum_rows):
        #num_print_cols is the number of columns to apply the sum formula to
        for col in range(start_col, start_col+num_print_cols):
            formula_string = (f"=sum({number_to_column_letter(col)}${row-num_sum_rows}"
                              f":{number_to_column_letter(col)}${row})")
            self.write_to_sheet(row, col, formula_string, format_name="sum_line")
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.sales_forecast_sheet.set_column('A:A', 5)  
        self.sales_forecast_sheet.set_column('B:B', 25) 
        
        # -- Headers and titles -- #
        
        #Page Title
        self.workbook_manager.validate_and_write(self.sales_forecast_sheet, 1, 1, 'Sales Forecast', format_name="title")
        
        # Create the color banner row
        self.sales_forecast_sheet.set_row(2, 5)
        for col in range(1, self.num_forecasted_years*12+5):
            self.write_to_sheet(2, col, "", format_name="color_banner")
        
        row=4
        
        #Model Titles
        self.write_to_sheet(row, self.annual_start_col, "Annual Model", format_name="bold")
        self.write_to_sheet(row, self.monthly_start_col, 'Monthly Model', format_name="bold")
        #Make the annual roll up
        
        row+=1
        
        ##----Headers----##
        #Annual Model
        col=self.annual_start_col
        for year in range(1, self.num_forecasted_years+1):
            self.write_to_sheet(row, self.annual_start_col+year-1, "Year "+str(year), format_name="plain")
            self.write_to_sheet(row+1, self.annual_start_col+year-1, '', format_name="bottom_border")
        
        #Monthly Model
        col=self.monthly_start_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                self.write_to_sheet(row, col, "Year "+str(year), format_name="plain")
                self.write_to_sheet(row+1, col, calendar.month_abbr[month], format_name="bottom_border")
                col+=1
        
        row+=2
        
        
        #------- Data and formulas -------#
        ##------ Revenue ------##
        self.write_to_sheet(row, 1, 'Revenue', format_name="italic")
        row+=1
        
        for recipe in self.business_object.sales_recipes:
            self.create_annual_sum_from_months_line(row, recipe, "price")
            self.create_monthly_forecast(row, recipe, "price")
            row+=1
            
        #Total Line
        self.write_to_sheet(row, 1, 'Total', format_name="text_right_align")
        sum_range=len(self.business_object.sales_recipes)
        self.create_total_line(row, self.annual_start_col, self.num_forecasted_years, sum_range)
        self.create_total_line(row, self.monthly_start_col, self.num_forecasted_years*12, sum_range)
        self.cell_manager.add_cell_reference(self.sheet_name, "Revenue", row=row, col=self.monthly_start_col) #Save the cell location
        row+=2
        
        ##------ Direct Costs ------##
        self.write_to_sheet(row, 1, 'Direct Costs', format_name="italic")
        row+=1
        
        for recipe in self.business_object.sales_recipes:
            self.create_annual_sum_from_months_line(row, recipe, "cost")
            self.create_monthly_forecast(row, recipe, "cost")
            row+=1
            
        #Total Line
        self.write_to_sheet(row, 1, 'Total', format_name="text_right_align")
        sum_range=len(self.business_object.sales_recipes)
        self.create_total_line(row, self.annual_start_col, self.num_forecasted_years, sum_range)
        self.create_total_line(row, self.monthly_start_col, self.num_forecasted_years*12, sum_range)
        self.cell_manager.add_cell_reference(self.sheet_name, "Direct_Costs", row=row, col=self.monthly_start_col) #Save the cell location
    
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:05:03 2024

@author: mikeg
"""

import calendar

from helper_functions import number_to_column_letter, get_cell_identifier

class SalesForecastPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.num_forecasted_years=workbook_manager.num_forecasted_years
        
        #Create the sheet
        self.sheet_name='Sales Forecast'
        self.workbook_manager.cell_info[self.sheet_name]={}
        self.sales_forecast_sheet = workbook_manager.add_sheet(self.sheet_name)#Make the sheet
        
        #Set start columns
        self.annual_start_col=2
        self.gap_between_annual_and_monthly=2 #Number of columns between last annual and first monthly
        self.monthly_start_col=self.annual_start_col+self.num_forecasted_years+self.gap_between_annual_and_monthly #Dynamically set the start cols
        
        self.populate_sheet()
        
    #-----------Function Definitions------------#
    def create_annual_sum_from_months_line(self, row, recipe, recipie_feature):
        #Annual forecast
        col=self.annual_start_col
        self.sales_forecast_sheet.write(row, col-1, recipe['name'])
        for col in range(2, 2+self.num_forecasted_years):
            formula_string = (f"=sumif($O6:$ZZ6, {number_to_column_letter(col)}6, "
                              f"$O{row + 1}:$ZZ{row + 1})"
                            ) #xlsxwriter indexes from 0, excel doesn't.
            self.workbook_manager.validate_and_write(self.sales_forecast_sheet, row, col, formula_string, format_name="currency")
            col+=1
            
    def create_monthly_forecast(self, row, recipe, recipie_feature):
        #Make the monthly forecast
        col=self.monthly_start_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                price_reference = self.cell_manager.get_cell_reference("Recipes", recipe['name'], recipie_feature, format_type='cell_ref', absolute_row=True)
                fraction_reference = self.cell_manager.get_cell_reference("Recipes", recipe['name'], "customer_fraction", format_type='cell_ref', absolute_row=True, absolute_col=True)
                customer_flow_reference=self.cell_manager.get_cell_reference("Customer Flow", 'monthly_visits',  format_type='cell_ref', absolute_row=True, absolute_col=True)
                formula_string = f"='Customer Flow'!{customer_flow_reference}*'recipes'!{price_reference}*'recipes'!{fraction_reference}"
                self.workbook_manager.validate_and_write(self.sales_forecast_sheet, row, col, formula_string, format_name="currency_cross") #Write the data
                col+=1
                
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.sales_forecast_sheet, row, col, formula_string, format_name, print_formula)
        
    def create_total_line(self, row, start_col, num_print_cols, num_sum_rows):
        #num_print_cols is the number of columns to apply the sum formula to
        for col in range(start_col, start_col+num_print_cols):
            formula_string = (f"=sum({number_to_column_letter(col)}${row-num_sum_rows}"
                              f":{number_to_column_letter(col)}${row})")
            self.write_to_sheet(row, col, formula_string, format_name="sum_line")
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.sales_forecast_sheet.set_column('A:A', 5)  
        self.sales_forecast_sheet.set_column('B:B', 25) 
        
        # -- Headers and titles -- #
        
        #Page Title
        self.workbook_manager.validate_and_write(self.sales_forecast_sheet, 1, 1, 'Sales Forecast', format_name="title")
        
        # Create the color banner row
        self.sales_forecast_sheet.set_row(2, 5)
        for col in range(1, self.num_forecasted_years*12+5):
            self.write_to_sheet(2, col, "", format_name="color_banner")
        
        row=4
        
        #Model Titles
        self.write_to_sheet(row, self.annual_start_col, "Annual Model", format_name="bold")
        self.write_to_sheet(row, self.monthly_start_col, 'Monthly Model', format_name="bold")
        #Make the annual roll up
        
        row+=1
        
        ##----Headers----##
        #Annual Model
        col=self.annual_start_col
        for year in range(1, self.num_forecasted_years+1):
            self.write_to_sheet(row, self.annual_start_col+year-1, "Year "+str(year), format_name="plain")
            self.write_to_sheet(row+1, self.annual_start_col+year-1, '', format_name="bottom_border")
        
        #Monthly Model
        col=self.monthly_start_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                self.write_to_sheet(row, col, "Year "+str(year), format_name="plain")
                self.write_to_sheet(row+1, col, calendar.month_abbr[month], format_name="bottom_border")
                col+=1
        
        row+=2
        
        
        #------- Data and formulas -------#
        ##------ Revenue ------##
        self.write_to_sheet(row, 1, 'Revenue', format_name="italic")
        row+=1
        
        for recipe in self.business_object.sales_recipes:
            self.create_annual_sum_from_months_line(row, recipe, "price")
            self.create_monthly_forecast(row, recipe, "price")
            row+=1
            
        #Total Line
        self.write_to_sheet(row, 1, 'Total', format_name="text_right_align")
        sum_range=len(self.business_object.sales_recipes)
        self.create_total_line(row, self.annual_start_col, self.num_forecasted_years, sum_range)
        self.create_total_line(row, self.monthly_start_col, self.num_forecasted_years*12, sum_range)
        self.cell_manager.add_cell_reference(self.sheet_name, "Revenue", row=row, col=self.monthly_start_col) #Save the cell location
        row+=2
        
        ##------ Direct Costs ------##
        self.write_to_sheet(row, 1, 'Direct Costs', format_name="italic")
        row+=1
        
        for recipe in self.business_object.sales_recipes:
            self.create_annual_sum_from_months_line(row, recipe, "cost")
            self.create_monthly_forecast(row, recipe, "cost")
            row+=1
            
        #Total Line
        self.write_to_sheet(row, 1, 'Total', format_name="text_right_align")
        sum_range=len(self.business_object.sales_recipes)
        self.create_total_line(row, self.annual_start_col, self.num_forecasted_years, sum_range)
        self.create_total_line(row, self.monthly_start_col, self.num_forecasted_years*12, sum_range)
        self.cell_manager.add_cell_reference(self.sheet_name, "Direct_Costs", row=row, col=self.monthly_start_col) #Save the cell location
    