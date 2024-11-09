import sys
import os

import xlsxwriter

#----Path Management----#
# Get the absolute path to the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)

# Get the parent directory (this would be your project root)
parent_dir = os.path.dirname(current_dir)
print(parent_dir)

# Add the current directory (where auto_financial_modeling.py is) to sys.path
sys.path.append(current_dir)

# Optionally, add the parent directory if you have imports from there as well
sys.path.append(parent_dir)


from business_entity_code import BusinessEntity
from helper_functions import FormatManager
from cellManager import CellManager

from recipes_page_code import RecipesPage
from data_page_code import DataPage
from title_page_code import TitlePage
from customer_flow_page_code import CustomerFlowPage
from sales_forecast_page_code import SalesForecastPage
from opex_capex_page_code import OpexCapexPage
from employee_page_code import EmployeePage
from unit_income_statement_code import UnitIncomePage
from unit_cash_flows_page_code import UnitCashFlowsPage
from consolidated_income_statement_code import ConsolidatedIncomeStatement
from consolidated_cash_flows_code import ConsolidatedCashFlowsPage
from comparables_quantitative_code import ComparablesQuantPage
from roll_out_code import RollOutPage






#----Create a workbook manager----#
class WorkbookManager:
    def __init__(self):
        self.name='Financial_Model.xlsx'
        # Create a new Excel file and add a worksheet
        self.workbook = xlsxwriter.Workbook(self.name)
        self.num_forecasted_years=10
        self.cell_info={}
        self.sheets = {}  # Dictionary to store worksheet references
        self.format_manager = FormatManager(self.workbook)  # Initialize formats once
        
    def add_sheet(self, sheet_name):
        sheet = self.workbook.add_worksheet(sheet_name)
        self.sheets[sheet_name] = sheet
        return sheet
    
    def close_workbook(self):
        # Save the workbook and close
       self.workbook.close()
        
    def validate_and_write(self, sheet, row, col, formula_string, format_name='plain', print_formula=False, url_display=None):
        """
        Validate and write data, formula, or URL to the specified cell.
        - If the input is a URL, write_url is used with optional display text.
        - Handles formula and plain data as well.
        
        Parameters:
        - sheet: The worksheet object where data is written.
        - row: The row index for writing.
        - col: The column index for writing.
        - formula_string: The data, formula, or URL to write.
        - format_name: The format to apply (default is 'plain').
        - print_formula: If set to True, formula is displayed instead of being calculated (for formulas only).
        - url_display: Optional display text for URLs (if provided).
        """
        # Get the format from the format manager
        cell_format = self.format_manager.get_format(format_name)
    
        # Check if the input is a URL (starts with 'http' or 'www')
        if isinstance(formula_string, str) and (formula_string.startswith('http') or formula_string.startswith('www')):
            # Write URL with optional display text
            display_text = url_display if url_display else formula_string
            sheet.write_url(row, col, formula_string, cell_format, display_text)
        elif isinstance(formula_string, str) and formula_string.startswith('='):
            # Check if it's an array formula
            if formula_string.startswith('={') and formula_string.endswith('}'):
                formula = formula_string[2:-1]  # Remove outer braces
                sheet.write_array_formula(row, col, row, col, formula, cell_format)
            else:
                # Write regular formula
                sheet.write_formula(row, col, formula_string, cell_format)
        else:
            # Write plain data
            sheet.write(row, col, formula_string, cell_format)

                
        



def generate_excel_model():
   
    
    #Main 
    workbook_manager1=WorkbookManager()

    cell_manager = CellManager()
    business_entity = BusinessEntity()

    #Make the pages
    #title_page=TitlePage(workbook_manager1, cell_manager, business_entity)
    data_page=DataPage(workbook_manager1, cell_manager, business_entity)
    recipes_page=RecipesPage(workbook_manager1, cell_manager, business_entity)
    customer_flow_page=CustomerFlowPage(workbook_manager1, cell_manager, business_entity)
    employee_page = EmployeePage(workbook_manager1, cell_manager, business_entity)
    opex_capex_page = OpexCapexPage(workbook_manager1, cell_manager, business_entity)
    sales_forecast_page = SalesForecastPage(workbook_manager1, cell_manager, business_entity)
    unit_income_page = UnitIncomePage(workbook_manager1, cell_manager, business_entity)
    unit_cash_flows_page = UnitCashFlowsPage(workbook_manager1, cell_manager, business_entity)
    comparables_quantative_page = ComparablesQuantPage(workbook_manager1, cell_manager, business_entity)
    roll_out_page = RollOutPage(workbook_manager1, cell_manager, business_entity)
    consolidated_income_statement_page = ConsolidatedIncomeStatement(workbook_manager1, cell_manager, business_entity)
    consolidated_cash_flows_page = ConsolidatedCashFlowsPage(workbook_manager1, cell_manager, business_entity)

   
    #Close the workbook 
    workbook_manager1.close_workbook()
    
    # Return the path to the generated Excel file so the site knows where to look for it
    file_path = os.path.join(os.getcwd(), 'Financial_Model.xlsx')
    print(f"File path is {file_path}")
    return file_path

if __name__ == "__main__":
    generate_excel_model()