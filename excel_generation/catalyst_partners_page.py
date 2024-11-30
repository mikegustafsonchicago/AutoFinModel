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
import time
import xlsxwriter
from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime

from business_entity_code import BusinessEntity
from cellManager import CellManager
from excel_generation.workbook_sheet_manager_code import WorkbookManager



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
        self.col_widths_dict = {
            'CORE': {
                'A': 2.59765625,
                'B': 32.59765625,
                'C': 21.59765625,
                'D': 20,
                'E': 20,
                'F': 20,
                'G': 20,
                'H': 4.19921875,
                'I': 18.0,
                'L': 2.59765625,
                'M': 9.0
            },
            'Input Page': {
                'A': 15.3984375,
                'B': 23.19921875
            },
            'Summary': {
                'A': 30.5,
                'B': 24.0,
                'C': 14.8984375,
                'D': 32.5,
                'E': 24.0,
                'F': 4.19921875,
                'G': 24.0,
                'H': 35.59765625,
                'I': 18.69921875,
                'J': 9.0,
                'N': 26.69921875,
                'O': 14.69921875,
                'P': 9.0,
                'Q': 9.0
            },
            'Performance Evaluation': {
                'A': 33.19921875,
                'B': 33.19921875,
                'C': 8.0,
                'D': 16.0,
                'E': 21.19921875,
                'F': 18.0,
                'G': 24.69921875,
                'H': 15.0,
                'I': 10.09765625,
                'J': 12.09765625,
                'K': 12.69921875,
                'L': 13.0,
                'N': 11.3984375,
                'O': 11.8984375,
                'P': 9.0,
                'Q': 14.19921875,
                'S': 9.0
            },
            'TR Summary for Packet': {
                'A': 21.69921875,
                'B': 13.8984375,
                'C': 13.59765625,
                'D': 11.3984375,
                'E': 7.8984375,
                'F': 9.5,
                'G': 10.0,
                'H': 10.0,
                'I': 10.0,
                'J': 10.0,
                'K': 9.0
            },
            'Historical Evaluation': {
                'A': 33.69921875,
                'B': 21.09765625,
                'E': 13.59765625,
                'F': 29.5,
                'G': 18.09765625,
                'H': 13.09765625,
                'I': 11.59765625,
                'M': 3.19921875,
                'N': 17.09765625,
                'O': 30.69921875,
                'Q': 15.8984375,
                'R': 10.0,
                'S': 12.5,
                'T': 13.19921875
            },
            'Future Assessment': {
                'A': 2.59765625,
                'B': 30.5,
                'C': 24.0,
                'D': 30,
                'E': 30,
                'F': 30,
                'G': 30,
                'H': 4.19921875,
                'I': 18.0,
                'L': 9.0
            },
            'Market Analysis': {
                'A': 2.59765625,
                'B': 30.5,
                'C': 24.0
            },
            'Human Capital': {
                'A': 40.09765625,
                'B': 28.5,
                'C': 14.3984375,
                'D': 13.7,
                'E': 48.09765625,
                'F': 4.8984375,
                'G': 31.8984375,
                'H': 12.8984375,
                'J': 15.09765625
            },
            'References': {
                'A': 32.09765625,
                'B': 14.0,
                'C': 15.5,
                'D': 20.8984375,
                'E': 26.0,
                'F': 27.19921875,
                'G': 81.59765625
            }
        }

        # Make the sheet
        self.xlsxwriter_sheet = self.workbook_manager.add_sheet(self.sheet_name)
        
        # Set column widths if they exist for this sheet
        if self.sheet_name in self.col_widths_dict:
            for col, width in self.col_widths_dict[self.sheet_name].items():
                self.xlsxwriter_sheet.set_column(f'{col}:{col}', width)
                
        self.populate_sheet()
        
   
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False, is_formula=False, url_display=None):
        self.workbook_manager.validate_and_write(self.xlsxwriter_sheet, row, col, formula_string, format_name, print_formula, url_display)
    

    def extend_format(self, row, start_col, end_col, format_name):
        """
        Extends a format across multiple columns in a row without writing text.
        
        Args:
            row (int): The row number to extend the format across
            start_col (int): The starting column number
            end_col (int): The ending column number (inclusive)
            format_name (str): The name of the format to apply
        """
        for col in range(start_col, end_col + 1):
            self.write_to_sheet(row, col, "", format_name=format_name)
    

class CORESheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='CORE'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(70)
        self.xlsxwriter_sheet.print_area('A1:L48')
        self.xlsxwriter_sheet.fit_to_pages(1, 1)
        self.xlsxwriter_sheet.set_row(0, 48)  # Set first row height
    
    def populate_sheet(self):
        
        # -- Headers and titles -- #
        # Merge A1:D3 for a title
        self.xlsxwriter_sheet.merge_range(0, 0, 2, 5, "")
        #Firm and Fund Names
        self.write_to_sheet(0, 0, "=('Input Page'!B2)", format_name="title")
        # Merge A1:D1 for a title
        self.xlsxwriter_sheet.merge_range(0, 7, 2, 10, "")
        self.write_to_sheet(0, 9, "=('Input Page'!B1)", format_name="title_right")
        
        
        # Create conclusion section head
        self.write_to_sheet(3, 0, 'Conclusion', format_name="section_header")
        self.extend_format(3, 1, 6, "section_header")
        
        self.write_to_sheet(9, 0, "CORE Opinion", format_name="paragraph_header")
        self.extend_format(9, 1, 6, "paragraph_header")
        
        self.write_to_sheet(11, 0, "Investment Capabilities", format_name="paragraph_header")
        self.extend_format(11, 1, 6, "paragraph_header")
        # Merge cells for Investment Capabilities section
        self.xlsxwriter_sheet.merge_range(12, 1, 20, 6, '', self.workbook_manager.format_manager.get_format('plain'))
        
        self.write_to_sheet(21, 0, "Operational Impact", format_name="paragraph_header")
        self.extend_format(21, 1, 6, "paragraph_header")
        # Merge cells for Operational Impact section
        self.xlsxwriter_sheet.merge_range(22, 1, 29, 6, '', self.workbook_manager.format_manager.get_format('plain'))
        
        self.write_to_sheet(30, 0, "Right Market", format_name="paragraph_header")
        self.extend_format(30, 1, 6, "paragraph_header")
        # Merge cells for Right Market section
        self.xlsxwriter_sheet.merge_range(31, 1, 37, 6, '', self.workbook_manager.format_manager.get_format('plain'))
        
        self.write_to_sheet(38, 0, "The Human Edge", format_name="paragraph_header")
        self.extend_format(38, 1, 6, "paragraph_header")
        # Merge cells for The Human Edge section
        self.xlsxwriter_sheet.merge_range(39, 1, 46, 6, '', self.workbook_manager.format_manager.get_format('plain'))
        
        
        # Create considerations section head
        self.write_to_sheet(3, 8, 'Considerations', format_name="section_header")
        #Extend the section head banner
        # Create the color banner after the title
        self.extend_format(3, 9, 10, "section_header")
        
        self.write_to_sheet(9, 8, "Team Work History", format_name="bold")
        self.write_to_sheet(11, 8, "Organic Growth Potential", format_name="bold")
        self.write_to_sheet(21, 8, "Operating Partner Economics", format_name="bold")




class InputSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Input Page'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(115)
        self.xlsxwriter_sheet.set_tab_color('#E5A128')
        self.xlsxwriter_sheet.print_area('A1:B4')
        self.xlsxwriter_sheet.fit_to_pages(1, 1)
    
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
        self.xlsxwriter_sheet.fit_to_pages(1, 1)
    
    def populate_sheet(self):
        #-------------Main-----------------------#
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
        self.extend_format(3, 1, 4, "section_header")
        
        self.xlsxwriter_sheet.merge_range(5, 0, 19, 4, "")
        
        # Create expected characteristics section head
        self.write_to_sheet(21, 0, 'EXPECTED PORTFOLIO CHARACTERISTICS', format_name="section_header")
        self.extend_format(21, 1, 4, "section_header")
            
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
        self.extend_format(35, 1, 4, "section_header")
        
        self.xlsxwriter_sheet.merge_range(37, 0, 42, 4, "")
        
        # Create firm fundamentals section head
        row = 3  # Starting row for the section
        col = 6  # Starting column for the section
        
        # Write the section header
        self.write_to_sheet(row, col, "FIRM", format_name="section_header")
        self.extend_format(row, col+1, col+2, "section_header")
        
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
            format_name = "unknown_value" if value == "-Not Provided-" else "plain_right"
            self.write_to_sheet(row, col + 2, value, format_name=format_name)
            
            # Increment row for the next entry
            row += 1
        
        # Create investment team section head
        self.write_to_sheet(row, col, "INVESTMENT TEAM", format_name="section_header")
        self.extend_format(row, col+1, col+2, "section_header")
        
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
            name = member.get("investment_team_member_name", "N/A")
            name_format = "unknown_value" if name == "-Not Provided-" else "plain"
            self.write_to_sheet(row, col, name, format_name=name_format)
            # Add comment with source for name
            source = member.get("source_string", "No source provided")
            self.xlsxwriter_sheet.write_comment(row, col, f"Source: {source}")
            
            title = member.get("investment_team_member_title", "N/A")
            title_format = "unknown_value" if title == "-Not Provided-" else "plain"
            self.write_to_sheet(row, col + 1, title, format_name=title_format)
            # Add comment with source for title
            self.xlsxwriter_sheet.write_comment(row, col + 1, f"Source: {source}")
            
            join_date = member.get("investment_team_member_join_date", "N/A")
            join_date_format = "unknown_value" if join_date == "-Not Provided-" else "plain_right"
            self.write_to_sheet(row, col + 2, join_date, format_name=join_date_format)
            # Add comment with source for join date
            self.xlsxwriter_sheet.write_comment(row, col + 2, f"Source: {source}")
            
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
        fees_data = self.business_object.fees_key_terms  # Extract the first dictionary from the list
        
        # Set starting row and column for the section
        row = 23  # Starting row for the section
        col = 6  # Starting column for the section
        
        # Write the section header
        self.write_to_sheet(row, col, "FUND FEES & KEY TERMS", format_name="section_header")
        self.extend_format(row, col+1, col+2, "section_header")
        
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
        seed_terms_data = self.business_object.seed_terms  # Extract the first dictionary from the list
        
        # Write the section header
        self.write_to_sheet(row, col, "SEED TERMS", format_name="section_header")
        self.extend_format(row, col+1, col+2, "section_header")
        
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

        # Create investment region and sector tables
        row = 2  # Starting row for the section
        col = 13  # Starting column (N)
        
        # Write Investment Region header
        self.write_to_sheet(row, col, "Investment Region", format_name="bold")
        row += 1
        
        # Write Investment Region data
        regions = [
            ("North America", 1.0),
            ("Europe", 0)
        ]
        for region, value in regions:
            self.write_to_sheet(row, col, region)
            self.write_to_sheet(row, col + 1, value, format_name = "percentage")
            row += 1
        
        row += 1  # Add spacing
        
        # Write Sector header 
        self.write_to_sheet(row, col, "Sector", format_name="bold")
        row += 1
        
        # Write Sector data
        sectors = [
            ("Consumer", 0),
            ("Education", 0),
            ("FinTech", 0), 
            ("Gov & Defense", 0),
            ("Healthcare", 0),
            ("Industrials", 0.5),
            ("Media", 0),
            ("Services", 0.5),
            ("SaaS", 0)
        ]
        
        for sector, value in sectors:
            self.write_to_sheet(row, col, sector)
            self.write_to_sheet(row, col + 1, value, format_name = "percentage")
            row += 1
        
        time.sleep(1) #Maybe just a delay will prevent asynchronous writing issues
        
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
        self.verticals_chart.set_title({'name': 'Sectors'})
        # Insert the chart into the worksheet
        self.xlsxwriter_sheet.insert_chart('D27', self.verticals_chart, {'x_scale': .5, 'y_scale': .5})
        

class PerformanceEvaluationSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Performance Evaluation'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(70)
        self.xlsxwriter_sheet.set_tab_color('#0F2749')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        # Write the section header
        row=0
        col=0
        for heading in ["Company", "Fund", "Industry", "Acquisition Method", "Acquisition Date", "Disposition Date", "Invested ($m)", "Realized", "Unrealized", "Total Value", "Net MOIC", "Net IRR", "Weight", ""]:
            
            self.write_to_sheet(row, col, heading, format_name="perf_section_header")
            col+=1
        col=0

        

class TRSummarySheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='TR Summary for Packet'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(100)
        self.xlsxwriter_sheet.set_tab_color('#176A93')
    
    def populate_sheet(self):
        #-------------Main-----------------------#


        # Write the section header
        row=0
        col=0
        for heading in ["Company", "Acquisition Date", "Status", "Invested ($m)", "Total Value", "Gross IRR 12/31/2019", "Gross MOIC 12/31/2019", "Estimated Net TVPI 12/31/2019"]:
            self.write_to_sheet(row, col, heading, format_name="section_header_small_wrap")
            col+=1
        col=0

class HistoricalEvaluationSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Historical Evaluation'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(70)
        self.xlsxwriter_sheet.set_tab_color('#FF0000')
        self.xlsxwriter_sheet.print_area('A1:O22')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_row(0, 48) 
        
        self.write_to_sheet(0, 0, "HISTORICAL EVALUATION", format_name="bold_page_header")
        self.extend_format(0, 1, 14, "bold_page_header")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 14, "=UPPER('Input Page'!B1)", format_name="bold")
        
        # Create section headers
        col=0
        for text in ["Company", "Fund", "Industry", "Acquisition Method", "Initial Investment", "Role", "", "Amount Invested (mm)", "Gross IRR", "Gross Realized MOIC", "Gross Unrealized MOIC", "Gross Total MOIC"]:
            self.write_to_sheet(3, col, text, format_name="section_header_small_wrap")
            col+=1



class FutureAssessmentSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Future Assessment'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(55)
        self.xlsxwriter_sheet.print_area('A1:K35')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_row(0, 48)  
        
        self.write_to_sheet(0, 0, "FUTURE ASSESSMENT", format_name="bold_page_header")
        self.extend_format(0, 1, 10, "bold_page_header")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 10, "=UPPER('Input Page'!B1)", format_name="bold")


        # Merge cells B5:G35
        self.xlsxwriter_sheet.merge_range('B5:G35', '', self.workbook_manager.format_manager.get_format('plain'))

        # Create a format for this specific text that includes text wrapping
        text_format = self.workbook_manager.workbook.add_format({
            'text_wrap': True,
            'align': 'left',
            'valign': 'top'
        })

        # Add "Investment Process" header with blue bar 
        self.write_to_sheet(3, 0, "Investment Process", format_name="section_header_small")
        self.extend_format(3, 1, 7, "section_header_small_wrap")
        # Write the text to the merged range (use the top-left cell of the merged range)
        self.write_to_sheet(4, 1, "Sourcing -\n\nSelection-\n\nManagement\n\nExiting\n\nDecision Authority\n\n")
        

        # Add "Service Providers" header with blue bar in columns J and K
        self.write_to_sheet(3, 8, "Service Providers", format_name="section_header_small")
        self.extend_format(3, 9, 10, "section_header_small_wrap")
        # Define the operations items and map them to service types
        operations_map = {
            "Audit": "Auditor",
            "Tax": "Tax",
            "Legal": "Legal Advisor", # Changed to match Legal Advisor
            "Fund Admin": "Fund Administrator", 
            "IT": "IT",
            "Compliance": "Compliance"
        }

        # Write each item starting at cell I5 (row 4, col 8)
        row = 4  # Starting at row 5 (zero-based)
        col = 8  # Column I

        # Create lookup dict of service providers, combining Legal Counsel and Legal Advisor
        service_providers = {}
        if self.business_object.service_providers:
            for provider in self.business_object.service_providers:
                service_type = provider["service_type"]
                # Normalize Legal Counsel to Legal Advisor
                if service_type == "Legal Counsel":
                    service_type = "Legal Advisor"
                service_providers[service_type] = {
                    "firm_name": provider["firm_name"],
                    "source": provider["source_string"]
                }

        # First write all mapped service types from operations_map
        for display_name, service_type in operations_map.items():
            self.write_to_sheet(row, col, display_name)
            if service_type in service_providers:
                provider_info = service_providers[service_type]
                self.write_to_sheet(row, col + 1, provider_info["firm_name"])
                # Add source as comment
                self.xlsxwriter_sheet.write_comment(row, col + 1, provider_info["source"])
            else:
                self.write_to_sheet(row, col + 1, "")
            row += 1

        # Then write any additional service providers not in operations_map
        for provider in self.business_object.service_providers:
            service_type = provider["service_type"]
            # Skip Legal Counsel since it's handled as Legal Advisor
            if service_type == "Legal Counsel":
                continue
            if service_type not in operations_map.values():
                self.write_to_sheet(row, col, service_type)
                self.write_to_sheet(row, col + 1, provider["firm_name"])
                # Add source as comment
                self.xlsxwriter_sheet.write_comment(row, col + 1, provider["source_string"])
                row += 1

        # Add "Debt Providers" header with blue bar in columns J and K
        self.write_to_sheet(17, 8, "Debt Providers", format_name="section_header_small")
        self.extend_format(17, 9, 10, "section_header_small_wrap")


class MarketAnalysisSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Market Analysis'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(60)
        self.xlsxwriter_sheet.print_area('A1:G31')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_row(0, 48) 

        self.write_to_sheet(0, 0, "MARKET ANALYSIS", format_name="bold_page_header")
        self.extend_format(0, 1, 14, "bold_page_header")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 14, "=UPPER('Input Page'!B1)", format_name="bold")


class HumanCapitalSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='Human Capital'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(50)
        self.xlsxwriter_sheet.print_area('A1:J39')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set row widths
        self.xlsxwriter_sheet.set_row(0, 48) 
        
        self.write_to_sheet(0, 0, "HUMAN CAPITAL", format_name="bold_page_header")
        self.extend_format(0, 1, 9, "bold_page_header")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 9, "=UPPER('Input Page'!B1)", format_name="bold")

        # Write section headers
        self.write_to_sheet(3, 0, "Summary", format_name="section_header")
        self.extend_format(3, 1, 4, "section_header")
        
        
        # Write Pending Hires column headers
        self.write_to_sheet(19, 0, "Pending Hires", format_name="section_header") 
        self.write_to_sheet(19, 1, "Title", format_name="section_header")
        self.write_to_sheet(19, 2, "Joining", format_name="section_header")
        self.write_to_sheet(19, 3, "", format_name="section_header")
        self.write_to_sheet(19, 4, "Relationship", format_name="section_header")

        # Write Expected Headcount column headers  
        self.write_to_sheet(23, 0, "Expected Headcount Expansions", format_name="section_header")
        self.write_to_sheet(23, 1, "Title", format_name="section_header")
        self.write_to_sheet(23, 2, "Expected Start", format_name="section_header")
        self.write_to_sheet(23, 3, "", format_name="section_header")
        self.write_to_sheet(23, 4, "Relationship", format_name="section_header")

        # Write Turnover column headers
        self.write_to_sheet(30, 0, "Turnover", format_name="section_header")
        self.write_to_sheet(30, 1, "Title", format_name="section_header")
        self.write_to_sheet(30, 2, "Joined", format_name="section_header")
        self.write_to_sheet(30, 3, "Departed", format_name="section_header")
        self.write_to_sheet(30, 4, "Reason for Leaving", format_name="section_header")

        # Write Firm history column headers
        self.write_to_sheet(3, 6, "Firm History & Milestones", format_name="section_header")
        self.extend_format(3, 7, 9, "section_header")


        # Write Firm Ownership section header
        self.write_to_sheet(16, 6, "Firm Ownership", format_name="section_header")
        self.extend_format(16, 7, 9, "section_header")
        
        # Write ownership data for each team member
        row = 17
        for member in self.business_object.investment_team:
            self.write_to_sheet(row, 6, member.get('investment_team_member_name', ''))
            self.write_to_sheet(row, 7, member.get('ownership', 0), format_name="percentage")
            row += 1
        
        # Write Carry Allocation section header
        row += 1
        self.write_to_sheet(row, 6, "Carry Allocation", format_name="section_header") 
        self.extend_format(row, 7, 9, "section_header")
        
        # Write carry data for each team member
        row += 1
        for member in self.business_object.investment_team:
            self.write_to_sheet(row, 6, member.get('investment_team_member_name', ''))
            self.write_to_sheet(row, 7, member.get('carry', 0), format_name="percentage")
            row += 1
        
        # Write Additional Strategies section header
        row += 1
        self.write_to_sheet(row, 6, "Additional Strategies", format_name="section_header")
        self.extend_format(row, 7, 9, "section_header")




class ReferencesSheet(Sheet):
    def __init__(self, workbook_manager, cell_manager, business_entity, sheet_name='References'):
        super().__init__(workbook_manager, cell_manager, business_entity, sheet_name)
        self.xlsxwriter_sheet.set_zoom(40)
        self.xlsxwriter_sheet.print_area('A1:G25')
    
    def populate_sheet(self):
        #-------------Main-----------------------#
        
        #Set column widths
        self.xlsxwriter_sheet.set_row(0, 48) 

        self.write_to_sheet(0, 0, "REFERENCES", format_name="bold_page_header")
        self.extend_format(0, 1, 6, "bold_page_header")
        self.write_to_sheet(1, 0, "=UPPER('Input Page'!B2)", format_name="bold")
        self.write_to_sheet(1, 6, "=UPPER('Input Page'!B1)", format_name="bold")
    
        headers = ["Reference", "On List?", "Date", "Company", "Title", "Relationship", "Key Takeaways"]
        for col, header in enumerate(headers):
            self.write_to_sheet(4, col, header, format_name="section_header")




def make_catalyst_summary():    
    try:
        # Print current working directory
        print(f"Current working directory: {os.getcwd()}")
        
        # Main 
        business_entity = BusinessEntity("catalyst")
        catalyst_workbook = WorkbookManager("catalyst_partners")
        cell_manager = CellManager()

        # Make the sheets
        sheets = [
            CORESheet(catalyst_workbook, cell_manager, business_entity, sheet_name='CORE'),
            InputSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Input Page'),
            summary_sheet := SummarySheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Summary'),
            PerformanceEvaluationSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Performance Evaluation'),
            TRSummarySheet(catalyst_workbook, cell_manager, business_entity, sheet_name='TR Summary for Packet'),
            HistoricalEvaluationSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Historical Evaluation'),
            FutureAssessmentSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Future Assessment'),
            MarketAnalysisSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Market Analysis'),
            HumanCapitalSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='Human Capital'),
            ReferencesSheet(catalyst_workbook, cell_manager, business_entity, sheet_name='References')
        ]
   
        # Close the workbook explicitly
        catalyst_workbook.close_workbook()
        
        # Get the full path to the generated file
        #file_path = os.path.join(os.getcwd(), catalyst_workbook.name)
        file_path = catalyst_workbook.output_path
        print(f"Excel file generated at: {file_path}")
        
        # Verify file exists and is not empty
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"File size: {file_size} bytes")
        else:
            print("Warning: File not found after generation!")
            
        return file_path
        
    except Exception as e:
        print(f"Error generating Excel file: {str(e)}")
        raise  # Re-raise the exception for the web handler to catch


if __name__ == "__main__":
    make_catalyst_summary()