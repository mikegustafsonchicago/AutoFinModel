# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:22:48 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier

class CustomerFlowPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.num_forecasted_years=workbook_manager.num_forecasted_years
       
        
        #Make the sheet
        self.sheet_name='Customer Flow'
        self.workbook_manager.cell_info[self.sheet_name]={}
        self.customer_flow_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        
        #Populate the sheet
        self.populate_sheet()
        
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.customer_flow_sheet, row, col, formula_string, format_name, print_formula)
    
    
    def populate_sheet(self): 
        #Set column widths
        self.customer_flow_sheet.set_column('A:A', 5)  
        self.customer_flow_sheet.set_column('B:B', 35)
        
        #Write the page title
        row=1
        col=1
        
        self.write_to_sheet(row, col, 'Customer Flow', format_name='title', print_formula=False)
        row+=1
        
        # Create the color banner row
        self.customer_flow_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet(2, col, "", format_name="color_banner")
        
        row=5
        col=1
            
        
        self.write_to_sheet(row, col, 'Customer visits are ', format_name='plain')
        self.write_to_sheet(row, col+1, self.business_object.customer_frequency, format_name='input')
        self.cell_manager.add_cell_reference(self.sheet_name, "customer_frequency",  row=row, col=col+3)#Save the cell location
        self.write_to_sheet(row, col+2, 'per hour', format_name='plain')
        row+=1
        
        self.write_to_sheet(row, col, 'Store is open ', format_name='plain')
        self.write_to_sheet(row, col+1, self.business_object.store_hours, format_name='input')
        self.cell_manager.add_cell_reference(self.sheet_name, "store_hours",  row=row, col=col+1)#Save the cell location
        self.write_to_sheet(row, col+2, 'hours per day', format_name='plain')
        row+=1
    
        self.write_to_sheet(row, col, 'Store is open ', format_name='plain')
        self.write_to_sheet(row, col+1, self.business_object.open_days, format_name='input')
        self.cell_manager.add_cell_reference(self.sheet_name, "open_days",  row=row, col=col+1)#Save the cell location
        self.write_to_sheet(row, col+2, 'days per month', format_name='plain')
        row+=1
        
        self.write_to_sheet(row, col, "Store gets ", format_name='plain')
        formula_string = "="+number_to_column_letter(col+1)+str(row)+ "*"+number_to_column_letter(col+1)+str(row-1)+ "*"+number_to_column_letter(col+1)+str(row-2)
        self.write_to_sheet(row, col+1, formula_string, "number")
        self.write_to_sheet(row, col+2, "customer visits monthly", format_name='plain')
        self.cell_manager.add_cell_reference(self.sheet_name, "monthly_visits",  row=row, col=col+1)#Save the cell location
        
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:22:48 2024

@author: mikeg
"""

from helper_functions import number_to_column_letter, get_cell_identifier

class CustomerFlowPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.num_forecasted_years=workbook_manager.num_forecasted_years
       
        
        #Make the sheet
        self.sheet_name='Customer Flow'
        self.workbook_manager.cell_info[self.sheet_name]={}
        self.customer_flow_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        
        #Populate the sheet
        self.populate_sheet()
        
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.customer_flow_sheet, row, col, formula_string, format_name, print_formula)
    
    
    def populate_sheet(self): 
        #Set column widths
        self.customer_flow_sheet.set_column('A:A', 5)  
        self.customer_flow_sheet.set_column('B:B', 35)
        
        #Write the page title
        row=1
        col=1
        
        self.write_to_sheet(row, col, 'Customer Flow', format_name='title', print_formula=False)
        row+=1
        
        # Create the color banner row
        self.customer_flow_sheet.set_row(2, 5)
        for col in range(1,10):
            self.write_to_sheet(2, col, "", format_name="color_banner")
        
        row=5
        col=1
            
        
        self.write_to_sheet(row, col, 'Customer visits are ', format_name='plain')
        self.write_to_sheet(row, col+1, self.business_object.customer_frequency, format_name='input')
        self.cell_manager.add_cell_reference(self.sheet_name, "customer_frequency",  row=row, col=col+3)#Save the cell location
        self.write_to_sheet(row, col+2, 'per hour', format_name='plain')
        row+=1
        
        self.write_to_sheet(row, col, 'Store is open ', format_name='plain')
        self.write_to_sheet(row, col+1, self.business_object.store_hours, format_name='input')
        self.cell_manager.add_cell_reference(self.sheet_name, "store_hours",  row=row, col=col+1)#Save the cell location
        self.write_to_sheet(row, col+2, 'hours per day', format_name='plain')
        row+=1
    
        self.write_to_sheet(row, col, 'Store is open ', format_name='plain')
        self.write_to_sheet(row, col+1, self.business_object.open_days, format_name='input')
        self.cell_manager.add_cell_reference(self.sheet_name, "open_days",  row=row, col=col+1)#Save the cell location
        self.write_to_sheet(row, col+2, 'days per month', format_name='plain')
        row+=1
        
        self.write_to_sheet(row, col, "Store gets ", format_name='plain')
        formula_string = "="+number_to_column_letter(col+1)+str(row)+ "*"+number_to_column_letter(col+1)+str(row-1)+ "*"+number_to_column_letter(col+1)+str(row-2)
        self.write_to_sheet(row, col+1, formula_string, "number")
        self.write_to_sheet(row, col+2, "customer visits monthly", format_name='plain')
        self.cell_manager.add_cell_reference(self.sheet_name, "monthly_visits",  row=row, col=col+1)#Save the cell location
        