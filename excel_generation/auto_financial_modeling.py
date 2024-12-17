import sys
import os
import xlsxwriter
import logging

#The helper functions sit in a different file from app.py
#So, if this code is run standalone, it doesn't need the path mangement below
#But, if it's run from app.py, it does need the path management below
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from helper_functions import FormatManager
from cellManager import CellManager
from business_entity_code import BusinessEntity
from recipes_page_code import RecipesPage
from revenue_cogs_build_code import RevenueCogsBuildPage
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
from valuation_comparables_code import ComparablesQuantPage
from roll_out_code import RollOutPage
from cell_reference_sheet_code import CellReferenceDebugPage
from excel_generation.workbook_sheet_manager_code import WorkbookManager



def generate_excel_model(debug_mode=False):
   
    debug_mode=True
    project_type = "financials"
    
    #Main 
    cell_manager = CellManager()
    workbook_manager1=WorkbookManager(project_type, cell_manager)

    
    business_entity = BusinessEntity("financials")

    #Make the pages
    #title_page=TitlePage(workbook_manager1, business_entity, "Title")
    #data_page=DataPage(workbook_manager1, business_entity, "Data")
    revenue_cogs_build_page=RevenueCogsBuildPage(workbook_manager1, business_entity, "Revenue_COGS_Build")
    #customer_flow_page=CustomerFlowPage(workbook_manager1, cell_manager, business_entity)
    employee_page = EmployeePage(workbook_manager1, business_entity, "Unit Employees")
    opex_capex_page = OpexCapexPage(workbook_manager1, cell_manager, business_entity)
    #sales_forecast_page = SalesForecastPage(workbook_manager1, cell_manager, business_entity)
    unit_income_page = UnitIncomePage(workbook_manager1, business_entity, "Unit_IS")
    unit_cash_flows_page = UnitCashFlowsPage(workbook_manager1, business_entity, "Unit_CF")
    comparables_quantative_page = ComparablesQuantPage(workbook_manager1, business_entity, "Valuation Comps")
    roll_out_page = RollOutPage(workbook_manager1, business_entity, "Roll Out")
    consolidated_income_statement_page = ConsolidatedIncomeStatement(workbook_manager1, business_entity, "Consolidated_IS")
    consolidated_cash_flows_page = ConsolidatedCashFlowsPage(workbook_manager1, business_entity, "Consolidated_CF")
    if debug_mode:
        cell_reference_debug_page = CellReferenceDebugPage(workbook_manager1, business_entity, "Cell_Reference_Debug")
   
    #Close the workbook 
    workbook_manager1.close_workbook()
    logging.info(f"Excel model created at {workbook_manager1.output_path}\n\n")
    
    # Return the file path from the workbook manager
    return workbook_manager1.output_path

if __name__ == "__main__":
    generate_excel_model()