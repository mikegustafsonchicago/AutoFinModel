# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 13:57:17 2024

@author: mikeg
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 08:38:38 2024

@author: mikeg
"""


import sys
import os
import logging
import xlsxwriter
from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime

from business_entity_code import BusinessEntity
from helper_functions import FormatManager
from cellManager import CellManager



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


#----Create a workbook manager----#
class WorkbookManager:
    def __init__(self):
        self.name='Catalyst_Partners_Summary.xlsx'
        # Create a new Excel file and add a worksheet
        self.workbook = xlsxwriter.Workbook(self.name)
        self.num_forecasted_years=10
        self.cell_info={}
        self.sheets = {}  # Dictionary to store worksheet references
        self.format_manager = FormatManager(self.workbook, config_file='catalystPartners.yaml')  # Initialize formats once
        
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





class Sheet:
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_entity  # Assign business_entity to self.business_object
        self.sheet_name = sheet_name
        self.workbook_manager.cell_info[self.sheet_name] = {}

        self.num_forecasted_years = workbook_manager.num_forecasted_years
        # Set start columns
        self.annual_year0_start = 8
        self.annual_hist_start = self.annual_year0_start  # Adding in some variables for historical values
        self.gap_between_annual_and_monthly = 2  # Number of columns between last annual and first monthly
        self.monthly_start_col = (
            self.annual_year0_start + self.num_forecasted_years + self.gap_between_annual_and_monthly
        )  # Dynamically set the start cols
        self.expenses_layout_start_col = 1  # The column that is the first for the details of the various expenses

        # Make the sheet
        self.xlsxwriter_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        self.populate_sheet()
        
   
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False, is_formula=False, url_display=None):
        self.workbook_manager.validate_and_write(self.xlsxwriter_sheet, row, col, formula_string, format_name, print_formula, url_display)
    

class CORESheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='CORE'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(70)
        self.xlsxwriter_sheet.print_area('A1:L48')
        self.xlsxwriter_sheet.fit_to_pages(1, 1)
    
    def populate_sheet(self):
        
        
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 2)  
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('C:C', 21)
        self.xlsxwriter_sheet.set_column('D:D', 21) 
        self.xlsxwriter_sheet.set_column('E:E', 21)
        self.xlsxwriter_sheet.set_column('F:F', 21)
        self.xlsxwriter_sheet.set_column('G:G', 21)
        self.xlsxwriter_sheet.set_column('H:H', 3.5)
        self.xlsxwriter_sheet.set_column('I:I', 17.3)
        self.xlsxwriter_sheet.set_column('J:J', 17.3)
        self.xlsxwriter_sheet.set_column('K:K', 17.3)
        self.xlsxwriter_sheet.set_column('L:L', 1.9)
        self.xlsxwriter_sheet.set_row(0, 48)
        
        # -- Headers and titles -- #
        # Merge A1:D3 for a title
        self.xlsxwriter_sheet.merge_range(0, 0, 2, 5, "")
        #Firm and Fund Names
        self.write_to_sheet(0, 0, "=('Input Page'!B2)", format_name="title")
        # Merge A1:D1 for a title
        self.xlsxwriter_sheet.merge_range(0, 9, 2, 10, "")
        self.write_to_sheet(0, 9, "=('Input Page'!B1)", format_name="title_right")
        
        
        # Create conclusion section head
        self.write_to_sheet(3, 0, 'Conclusion', format_name="section_header")
        #Extend the section head banner
        # Create the color banner row
        for col in range(1,10):
            self.write_to_sheet(3, col, "", format_name="section_header")
        
        self.write_to_sheet(9, 0, "CORE Opinion", format_name="paragraph_header")
        for col in range(1,6):
            self.write_to_sheet(9, col, "", format_name="paragraph_header") #Extend the  bottom border line
        self.write_to_sheet(11, 0, "Investment Capabilities", format_name="paragraph_header")
        for col in range(1,6):
            self.write_to_sheet(11, col, "", format_name="paragraph_header") #Extend the  bottom border line
        self.write_to_sheet(21, 0, "Operational Impact", format_name="paragraph_header")
        for col in range(1,6):
            self.write_to_sheet(21, col, "", format_name="paragraph_header") #Extend the  bottom border line
        self.write_to_sheet(30, 0, "Right Market", format_name="paragraph_header")
        for col in range(1,6):
            self.write_to_sheet(30, col, "", format_name="paragraph_header") #Extend the  bottom border line
        self.write_to_sheet(38, 0, "The Human Edge", format_name="paragraph_header")
        for col in range(1,6):
            self.write_to_sheet(38, col, "", format_name="paragraph_header") #Extend the  bottom border line
        
        
        # Create considerations section head
        self.write_to_sheet(3, 8, 'Considerations', format_name="section_header")
        #Extend the section head banner
        # Create the color banner after the title
        self.write_to_sheet(3, 9, "", format_name="section_header")
        self.write_to_sheet(3, 10, "", format_name="section_header")
        self.write_to_sheet(9, 8, "Team Work History", format_name="bold")
        self.write_to_sheet(11, 8, "Organic Growth Potential", format_name="bold")
        self.write_to_sheet(21, 8, "Operating Partner Economics", format_name="bold")




class InputSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Inputs'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(115)
        self.xlsxwriter_sheet.set_tab_color('#E5A128')
        self.xlsxwriter_sheet.print_area('A1:B4')
        
        
        
        
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 14.7)  
        self.xlsxwriter_sheet.set_column('B:B', 22.5) 
        
        self.write_to_sheet(0, 0, 'Fund Name')
        self.write_to_sheet(1, 0, 'GP Name')
        self.write_to_sheet(2, 0, 'Primary Office')
        self.write_to_sheet(3, 0, 'Year Founded')
        self.write_to_sheet(0, 1, 'Fund I')
        self.write_to_sheet(1, 1, 'Cross Rapids Capital')
        self.write_to_sheet(2, 1, 'New York, NY')
        self.write_to_sheet(3, 1, '2020')
        

class SummarySheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Summary'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(70)
        self.xlsxwriter_sheet.print_area('A1:I47')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        logging.debug(f"SUMMARY. Here's the business object {self.business_object}")
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 29.8)  
        self.xlsxwriter_sheet.set_column('B:B', 23.3) 
        self.xlsxwriter_sheet.set_column('C:C', 21)
        self.xlsxwriter_sheet.set_column('D:D', 31.8) 
        self.xlsxwriter_sheet.set_column('E:E', 21)
        self.xlsxwriter_sheet.set_column('F:F', 3.5)
        self.xlsxwriter_sheet.set_column('G:G', 23)
        self.xlsxwriter_sheet.set_column('H:H', 35)
        self.xlsxwriter_sheet.set_column('I:I', 18)
        self.xlsxwriter_sheet.set_column('J:J', 17.3)
        self.xlsxwriter_sheet.set_column('K:K', 17.3)
        self.xlsxwriter_sheet.set_column('L:L', 1.9)
        self.xlsxwriter_sheet.set_column('N:N', 26)
        self.xlsxwriter_sheet.set_column('O:O', 14)
        self.xlsxwriter_sheet.set_row(0, 46.8) 
        

        # -- Headers and titles -- #
        # Merge A1:D3 for a title
        self.xlsxwriter_sheet.merge_range(0, 0, 2, 3, "")
        #Firm and Fund Names
        self.write_to_sheet(0, 0, "=('Input Page'!B2)", format_name="title")
        # Merge H1:I1 for a title
        self.xlsxwriter_sheet.merge_range(0, 7, 2, 8, "")
        self.write_to_sheet(0, 7, "=('Input Page'!B1)", format_name="title_right")
        
        
        # Create overview section head
        self.write_to_sheet(3, 0, 'OVERVIEW', format_name="section_header")
        #Extend the section head banner
        # Create the color banner row
        for col in range(1,5):
            self.write_to_sheet(3, col, "", format_name="section_header")
        
        
        # Create expected characteristics section head
        self.write_to_sheet(21, 0, 'EXPECTED PORTFOLIO CHARACTERISTICS', format_name="section_header")
        #Extend the section head banner
        # Create the color banner row
        for col in range(1,5):
            self.write_to_sheet(21, col, "", format_name="section_header")
            
        #Populate the data
        self.write_to_sheet(22, 0, "Primary Strategy", format_name="bold")
        self.write_to_sheet(22, 1, "Unknown", format_name="plain_right")
        self.write_to_sheet(23, 0, "Positions", format_name="bold")
        self.write_to_sheet(23, 1, "Unknown", format_name="plain_right")
        self.write_to_sheet(24, 0, "Entry/EBITDA", format_name="bold")
        self.write_to_sheet(24, 1, "Unknown", format_name="plain_right")
        self.write_to_sheet(22, 3, "Check Size", format_name="bold")
        self.write_to_sheet(22, 4, "Unknown", format_name="plain_right")
        self.write_to_sheet(23, 3, "Target Gross/Net IRR", format_name="bold")
        self.write_to_sheet(23, 4, "Unknown", format_name="plain_right")
        self.write_to_sheet(24, 3, "Target Gross/Net IRR", format_name="bold")
        self.write_to_sheet(24, 4, "Unknown", format_name="plain_right")
           
            
        # Create proposed seeding/value add section head
        self.write_to_sheet(35, 0, 'PROPOSED SEEDING & CATALYST VALUE-ADD', format_name="section_header")
        #Extend the section head banner
        # Create the color banner row
        for col in range(1,5):
            self.write_to_sheet(35, col, "", format_name="section_header")
        
        
        
        # Create firm fundamentals section head
        row = 3  # Starting row for the section
        col = 6  # Starting column for the section
        
        # Write the section header
        self.write_to_sheet(row, col, "FIRM", format_name="section_header")
        self.write_to_sheet(row, col+1, "", format_name="section_header")
        self.write_to_sheet(row, col+2, "", format_name="section_header")
        row += 2  # Leave a row for spacing
        
        # Write table headers
        fundamentals_json_to_firm_table_dict = {
        "founded_year": "Founded",
        "primary_office": "Primary Office",
        "ownership_structure": "Ownership",
        "total_employees": "Employees",
        "diversity_status": "Diversity Status",
        "website": "Website",
        }

        fundamentals_data = self.business_object.fundamentals[0]  # Extract the first dictionary from the list

        for key, header in fundamentals_json_to_firm_table_dict.items():
            # Write header in the first column
            self.write_to_sheet(row, col, header, format_name="bold")
            
            # Write corresponding data from JSON in the second column
            value = fundamentals_data.get(key, "N/A")
            self.write_to_sheet(row, col + 2, value, format_name="plain_right")
            
            # Increment row for the next entry
            row += 1
    
        
        
        
        
        # Create investment team section head
        self.write_to_sheet(row, col, "INVESTMENT TEAM", format_name="section_header")
        self.write_to_sheet(row, col+1, "", format_name="section_header")
        self.write_to_sheet(row, col+2, "", format_name="section_header")
        row+=1
        self.write_to_sheet(row, col, "Total Professionals", format_name="bold")
        self.write_to_sheet(row, col+1, len(self.business_object.investment_team), format_name="plain")
        row += 2  # Leave a row for spacing
        
        # Write table headers
        headers = ["Name", "Title", "Joined Firm"]
        for i, header in enumerate(headers):
            self.write_to_sheet(row, col + i, header, format_name="bold_underline")
        row += 1
        
        # Write investment team data dynamically
        for member in self.business_object.investment_team:
            self.write_to_sheet(row, col, member.get("investment_team_member_name", "N/A"), format_name="plain")
            self.write_to_sheet(row, col + 1, member.get("investment_team_member_title", "N/A"), format_name="plain")
            self.write_to_sheet(row, col + 2, member.get("investment_team_member_join_date", "N/A"), format_name="plain_right")
            row += 1




        # Define the mapping dictionary
        fees_json_to_table_dict = {
            "currency": "Currency",
            "target_fundraise": "Target Fundraise",
            "management_fee": "Management Fee",
            "carried_interest": "Carried Interest",
            "preferred_return": "Preferred Return",
            "investment_period": "Investment Period",
            "fund_term": "Fund Term",
            "GP_commitment": "GP Commitment",
            "GP_commitment_funding_source": "GP Commitment Funding Source"
        }
        
        # Access the fees data from the JSON file
        fees_data = self.business_object.fees_key_terms[0]  # Extract the first dictionary from the list
        
        # Set starting row and column for the section
        row = 23  # Starting row for the section
        col = 6  # Starting column for the section
        
        # Write the section header
        self.write_to_sheet(row, col, "FUND FEES & KEY TERMS", format_name="section_header")
        self.write_to_sheet(row, col + 1, "", format_name="section_header")
        self.write_to_sheet(row, col + 2, "", format_name="section_header")
        row += 2  # Leave a row for spacing
        
        # Iterate through the dictionary and write each header and corresponding JSON value
        for key, header in fees_json_to_table_dict.items():
            # Write header in the first column
            self.write_to_sheet(row, col, header, format_name="bold")
            
            # Write corresponding data from JSON in the adjacent column
            value = fees_data.get(key, "N/A")
            self.write_to_sheet(row, col + 2, value, format_name="plain_right")
            
            # Increment row for the next entry
            row += 1
            
            
        # Define the mapping dictionary for seed terms
        seed_terms_json_to_table_dict = {
            "expense_name": "Target Seed Investment",
            "initial_investment": "Initial Seed Investment",
            "fundraising_date": "Seed Fundraising Timeline",
            "revenue_share": "Revenue Share",
            "revenue_share_cap": "Revenue Share Cap",
            "revenue_share_tail": "Revenue Share Tail"
        }
        
        # Access the seed terms data from the JSON file
        seed_terms_data = self.business_object.seed_terms[0]  # Extract the first dictionary from the list
        
        # Write the section header
        self.write_to_sheet(row, col, "SEED TERMS", format_name="section_header")
        self.write_to_sheet(row, col + 1, "", format_name="section_header")
        self.write_to_sheet(row, col + 2, "", format_name="section_header")
        row += 2  # Leave a row for spacing
        
        # Iterate through the dictionary and write each header and corresponding JSON value
        for key, header in seed_terms_json_to_table_dict.items():
            # Write header in the first column
            self.write_to_sheet(row, col, header, format_name="bold")
            
            # Write corresponding data from JSON in the adjacent column
            value = seed_terms_data.get(key, "N/A")
            self.write_to_sheet(row, col + 2, value, format_name="plain_right")
            
            # Increment row for the next entry
            row += 1
        
        
       # Create a pie chart object for the regions chart
        self.regions_chart = self.workbook_manager.workbook.add_chart({'type': 'pie'})
        # Configure the chart series
        self.regions_chart.add_series({
            'name': 'Investment Regions',
            'categories': '=Summary!$N$4:$N$5',  # Set the categories
            'values': '=Summary!$O$4:$O$5',      # Set the values
        })
        # Add a title
        self.regions_chart.set_title({'name': 'Investment Regions'})
        # Insert the chart into the worksheet
        self.xlsxwriter_sheet.insert_chart('A27', self.regions_chart, {'x_scale': .5, 'y_scale': .5})
        
        
        
        # Create a pie chart object for the regions chart
        self.verticals_chart = self.workbook_manager.workbook.add_chart({'type': 'pie'})
        # Configure the chart series
        self.verticals_chart.add_series({
            'name': 'Sectors',
            'categories': '=Summary!$N$8:$N$16',  # Set the categories
            'values': '=Summary!$O$8:$O$16',      # Set the values
        })
        # Add a title
        self.regions_chart.set_title({'name': 'Sectors'})
        # Insert the chart into the worksheet
        self.xlsxwriter_sheet.insert_chart('D27', self.verticals_chart, {'x_scale': .5, 'y_scale': .5})
        

class PerformanceEvaluationSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Performance Evaluation'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(70)
        self.xlsxwriter_sheet.set_tab_color('#0F2749')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 2)  
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('C:C', 21)
        self.xlsxwriter_sheet.set_column('D:D', 21) 
        self.xlsxwriter_sheet.set_column('E:E', 21)
        self.xlsxwriter_sheet.set_column('F:F', 21)
        self.xlsxwriter_sheet.set_column('G:G', 21)
        self.xlsxwriter_sheet.set_column('H:H', 3.5)
        self.xlsxwriter_sheet.set_column('I:I', 17.3)
        self.xlsxwriter_sheet.set_column('J:J', 17.3)
        self.xlsxwriter_sheet.set_column('K:K', 17.3)
        self.xlsxwriter_sheet.set_column('L:L', 1.9)
        

        

class TRSummarySheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='TR Summary for Packet'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(70)
        self.xlsxwriter_sheet.set_tab_color('#176A93')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 2)  
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('C:C', 21)
        self.xlsxwriter_sheet.set_column('D:D', 21) 
        self.xlsxwriter_sheet.set_column('E:E', 21)
        self.xlsxwriter_sheet.set_column('F:F', 21)
        self.xlsxwriter_sheet.set_column('G:G', 21)
        self.xlsxwriter_sheet.set_column('H:H', 3.5)
        self.xlsxwriter_sheet.set_column('I:I', 17.3)
        self.xlsxwriter_sheet.set_column('J:J', 17.3)
        self.xlsxwriter_sheet.set_column('K:K', 17.3)
        self.xlsxwriter_sheet.set_column('L:L', 1.9)



class HistoricalEvaluationSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Historical Evaluation'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(70)
        self.xlsxwriter_sheet.set_tab_color('#FF0000')
        self.xlsxwriter_sheet.print_area('A1:O22')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 33)  
        self.xlsxwriter_sheet.set_column('B:B', 20) 
        self.xlsxwriter_sheet.set_column('C:C', 20)
        self.xlsxwriter_sheet.set_column('D:D', 20) 
        self.xlsxwriter_sheet.set_column('E:E', 13)
        self.xlsxwriter_sheet.set_column('F:F', 29)
        self.xlsxwriter_sheet.set_column('G:G', 17)
        self.xlsxwriter_sheet.set_column('H:H', 12)
        self.xlsxwriter_sheet.set_column('I:I', 12)
        self.xlsxwriter_sheet.set_column('J:J', 12)
        self.xlsxwriter_sheet.set_column('K:K', 12)
        self.xlsxwriter_sheet.set_column('L:L', 12)
        self.xlsxwriter_sheet.set_column('M:M', 3)
        self.xlsxwriter_sheet.set_column('N:N', 16)
        self.xlsxwriter_sheet.set_column('O:O', 30)
        self.xlsxwriter_sheet.set_row(0, 48) 
        
        self.write_to_sheet(0, 0, "HISTORICAL EVALUATION", format_name="size_eighteen_bold")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 14, "=UPPER('Input Page'!B1)", format_name="bold")
        
        # Create section headers
        col=0
        for text in ["Company", "Fund", "Industry", "Acquisition Method", "Initial Investment", "Role", "", "Amount Invested (mm)", "Gross IRR", "Gross Realized MOIC", "Gross Unrealized MOIC", "Gross Total MOIC"]:
            self.write_to_sheet(3, col, text, format_name="section_header")
            col+=1



class FutureAssessmentSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Future Assessment'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(55)
        self.xlsxwriter_sheet.print_area('A1:K35')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 2)  
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('C:C', 21)
        self.xlsxwriter_sheet.set_column('D:D', 21) 
        self.xlsxwriter_sheet.set_column('E:E', 21)
        self.xlsxwriter_sheet.set_column('F:F', 21)
        self.xlsxwriter_sheet.set_column('G:G', 21)
        self.xlsxwriter_sheet.set_column('H:H', 3.5)
        self.xlsxwriter_sheet.set_column('I:I', 17.3)
        self.xlsxwriter_sheet.set_column('J:J', 17.3)
        self.xlsxwriter_sheet.set_column('K:K', 17.3)
        self.xlsxwriter_sheet.set_column('L:L', 1.9)
        self.xlsxwriter_sheet.set_row(0, 48)  
        
        self.write_to_sheet(0, 0, "FUTURE ASSESSMENT", format_name="size_eighteen_bold")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 10, "=UPPER('Input Page'!B1)", format_name="bold")



class MarketAnalysisSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Market Analysis'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(60)
        self.xlsxwriter_sheet.print_area('A1:G31')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 2)  
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('C:C', 21)
        self.xlsxwriter_sheet.set_column('D:D', 21) 
        self.xlsxwriter_sheet.set_column('E:E', 21)
        self.xlsxwriter_sheet.set_column('F:F', 21)
        self.xlsxwriter_sheet.set_column('G:G', 21)
        self.xlsxwriter_sheet.set_column('H:H', 3.5)
        self.xlsxwriter_sheet.set_column('I:I', 17.3)
        self.xlsxwriter_sheet.set_column('J:J', 17.3)
        self.xlsxwriter_sheet.set_column('K:K', 17.3)
        self.xlsxwriter_sheet.set_column('L:L', 1.9)
        self.xlsxwriter_sheet.set_row(0, 48) 
        
        self.write_to_sheet(0, 0, "MARKET ANALYSIS", format_name="size_eighteen_bold")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 14, "=UPPER('Input Page'!B1)", format_name="bold")


class HumanCapitalSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Human Capital'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(50)
        self.xlsxwriter_sheet.print_area('A1:J39')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 2)  
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('C:C', 21)
        self.xlsxwriter_sheet.set_column('D:D', 21) 
        self.xlsxwriter_sheet.set_column('E:E', 21)
        self.xlsxwriter_sheet.set_column('F:F', 21)
        self.xlsxwriter_sheet.set_column('G:G', 21)
        self.xlsxwriter_sheet.set_column('H:H', 3.5)
        self.xlsxwriter_sheet.set_column('I:I', 17.3)
        self.xlsxwriter_sheet.set_column('J:J', 17.3)
        self.xlsxwriter_sheet.set_column('K:K', 17.3)
        self.xlsxwriter_sheet.set_column('L:L', 1.9)
        self.xlsxwriter_sheet.set_row(0, 48) 
        
        self.write_to_sheet(0, 0, "HUMAN CAPITAL", format_name="size_eighteen_bold")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 9, "=UPPER('Input Page'!B1)", format_name="bold")


class ReferencesSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='References'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(40)
        self.xlsxwriter_sheet.print_area('A1:G25')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 2)  
        self.xlsxwriter_sheet.set_column('B:B', 25) 
        self.xlsxwriter_sheet.set_column('C:C', 21)
        self.xlsxwriter_sheet.set_column('D:D', 21) 
        self.xlsxwriter_sheet.set_column('E:E', 21)
        self.xlsxwriter_sheet.set_column('F:F', 21)
        self.xlsxwriter_sheet.set_column('G:G', 21)
        self.xlsxwriter_sheet.set_column('H:H', 3.5)
        self.xlsxwriter_sheet.set_column('I:I', 17.3)
        self.xlsxwriter_sheet.set_column('J:J', 17.3)
        self.xlsxwriter_sheet.set_column('K:K', 17.3)
        self.xlsxwriter_sheet.set_column('L:L', 1.9)
        self.xlsxwriter_sheet.set_row(0, 48) 

        self.write_to_sheet(0, 0, "REFERENCES", format_name="size_eighteen_bold")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 6, "=UPPER('Input Page'!B1)", format_name="bold")



def make_catalyst_summary():    
    #Main 
    business_entity = BusinessEntity()
    catalyst_workbook=WorkbookManager()
    cell_manager = CellManager()

    #Make the sheets
    CORE_sheet=CORESheet(catalyst_workbook, cell_manager, business_entity, sheet_name='CORE')
    input_sheet=InputSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Input Page')
    summary_sheet=SummarySheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Summary')
    performance_evaluation_sheet=PerformanceEvaluationSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Performance Evaluation')
    TR_summary_sheet=TRSummarySheet(catalyst_workbook, cell_manager, business_entity, sheet_name='TR Summary for Packet')
    historical_evaluation_sheet=HistoricalEvaluationSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Historical Evaluation')
    future_assessment_sheet=FutureAssessmentSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Future Assessment')
    market_analysis_sheet=MarketAnalysisSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Market Analysis')
    human_capital_sheet=HumanCapitalSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Human Capital')
    references_sheet=ReferencesSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='References')

   
    #Close the workbook 
    catalyst_workbook.close_workbook()
    
    # Return the path to the generated Excel file so the site knows where to look for it
    file_path = os.path.join(os.getcwd(), catalyst_workbook.name)
    return file_path



summary_text = {"CORE":
                {"IC": "The team has expertise across multiple transaction types, all of which are predicated on solving for an element of complexity. The Partners' track record at Centerbridge includes over $700 million invested across six core deals that returned 2.4x gross, or 1.9x net if you assume a typical gross-to-net spread. That’s top quartile vs. similar vintage buyout funds (the five realized deals returned 2.7x gross, 2.2x net)1, with underlying equity value driven primarily through EBITDA growth. These strong results came despite limited growth through small accretive add-ons, which is something CRC will flexibly pursue to optimize their target MOIC.  Kyle was responsible for two turnarounds at Centerbridge where he was placed on the deals after they had underperformed. In one case, ATU, Kyle helped the firm avoid a large negative liability and recouped a small portion of the cost basis (0.1x MOIC). This speaks to his ability to negotiate complexity and find value, even in difficult situations.",
                 "OI": "Their approach to operations is hands-on. Ben immerses himself in each portfolio company for the first 2-3 months of CRC's ownership period, at which point day-to-day oversight is left to the CEO and a Transformation Officer that CRC selects in tandem with the CEO. The company directly hires the Transformation Officer, but they are intended to roll off after exit, and these individuals will start to foster a pool of talent that CRC can tap for future portfolio company engagements. The team’s experience at larger, process-driven firms like Centerbridge and Platinum helps inform their current approach to portfolio company operations. This level of sophistication is unique for an emerging manager and for the lower middle market, which should leave CRC competitively positioned.",
                 "RM": "The Firm's target market has evolved over the last 10 years in a way that should facilitate high quality deal flow without the team needing to lean into the DFC-style investments that were prevalent during their time at Centerbridge, but which are outside of our preferred scope and can result in inconsistent entry value relative to normalized EBITDA. CRC's opportunity set is augmented by the influx in large corporates seeking to de-risk their balance sheets by selling non-core divisions. CRC is not reliant upon this deal flow for success, but it creates an attractive sourcing channel and entry point for the Firm. ",
                 "HE": "Kyle and Mina worked directly together at Centerbridge, jointly executing five investments over an eight-year period. This provides a high degree of continuity, particularly since Mina chose to leave Carlyle shortly into her tenure to rejoin Kyle at CRC. Over the last three years, Kyle and Mina have also proven an ability to partner collaboratively with Ben, which provides comfort around their working relationship despite Ben not sharing time with them at Centerbridge. Kyle and Mina have invested significant personal money to fund CRC's working capital and support the firm's first two portfolio companies. This excludes their planned GP commitment, which will be 3% of total commitments and funded in cash. This creates strong economic alignment between CRC and its future investors. "

                        }
                }


if __name__ == "__main__":
    make_catalyst_summary()