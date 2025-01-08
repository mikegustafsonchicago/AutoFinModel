import os
import xlsxwriter
from datetime import datetime
import calendar
import sys

# Add parent directory to path to import file_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from file_manager import upload_file_to_s3, get_project_outputs_path
from helper_functions import FormatManager, number_to_column_letter, get_cell_identifier

#----Workbook Manager----#
# The WorkbookManager deals with all the details that span across a worksheet:
# It should not hold business-specific information. That's for the business entity class.
# - Creating and managing Excel workbooks with proper file paths and names
# - Managing worksheet creation and access
# - Applying consistent formatting across worksheets
# - Validating and writing data, formulas, and URLs to cells
# - Closing and saving workbooks properly
class WorkbookManager:
    def __init__(self, project_type, cell_manager):
        self.cell_manager = cell_manager

        #Name the workbook based on the project name
        if project_type == "financials":
            self.name = 'Financial_Model.xlsx'
        elif project_type == "catalyst_partners":
            self.name = 'Catalyst_Partners_Summary.xlsx'
        else:
            raise ValueError(f"Invalid project name: {project_type}")
        
        # Create local temp directory for Excel generation
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        self.temp_dir = os.path.join(parent_dir, 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)

        # Set temporary local path for workbook creation
        self.local_path = os.path.join(self.temp_dir, self.name)
        
        # Get S3 output path
        s3_outputs_path = get_project_outputs_path()
        self.s3_path = f"{s3_outputs_path}/{self.name}" if s3_outputs_path else None
        
        # Create workbook
        print(f"Creating Excel file temporarily at: {self.local_path}")
        self.workbook = xlsxwriter.Workbook(self.local_path)
        
        self.num_forecasted_years=10
        self.cell_info={}
        self.sheets = {}  # Dictionary to store worksheet references

        if project_type == "financials":    
            self.format_manager = FormatManager(self.workbook)
        elif project_type == "catalyst_partners":
            self.format_manager = FormatManager(self.workbook, config_file='catalystPartners.yaml')

    def add_sheet(self, sheet_name):
        sheet = self.workbook.add_worksheet(sheet_name)
        self.sheets[sheet_name] = sheet
        return sheet
    
    def close_workbook(self):
        # Save and close the workbook
        self.workbook.close()
        
        # Upload to S3 if path is available
        if self.s3_path:
            if upload_file_to_s3(self.local_path, self.s3_path):
                print(f"Successfully uploaded workbook to S3: {self.s3_path}")
                self.output_path = self.s3_path  # Use S3 path as output path
            else:
                print("Failed to upload to S3, using local path")
                self.output_path = self.local_path
        else:
            print("No S3 path available, using local path")
            self.output_path = self.local_path

        # Clean up temporary file
        try:
            os.remove(self.local_path)
            print(f"Cleaned up temporary file: {self.local_path}")
        except Exception as e:
            print(f"Failed to clean up temporary file: {e}")
        
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



class SheetManager:
    def __init__(self, workbook_manager, business_object, sheet_name):
        self.workbook_manager = workbook_manager
        self.business_object = business_object
        self.cell_manager = self.workbook_manager.cell_manager
        
        self.sheet_name = sheet_name
        self.xlsxwriter_sheet = self.workbook_manager.add_sheet(sheet_name)
        

        self.num_forecasted_years=self.workbook_manager.num_forecasted_years
        self.num_hist_years = len(self.business_object.historical_financials) if self.business_object.historical_financials else 0
     #--------Function Definitions--------#
    def create_annual_sum_from_months_line(self, row):
        for col in range(self.annual_start_col, self.annual_start_col+self.num_forecasted_years):
            if_row = self.cell_manager.get_cell_reference(self.sheet_name, "Headers", "Annual", format_type="row")
            
            # Get the first and last monthly columns dynamically
            first_monthly_col = number_to_column_letter(self.monthly_start_col)
            last_monthly_col = number_to_column_letter(self.monthly_start_col + (12 * self.num_forecasted_years) - 1)
            
            formula_string = (f"=sumif({first_monthly_col}{if_row}:{last_monthly_col}{if_row}, "
                             f"{number_to_column_letter(col)}{if_row}, "
                             f"{first_monthly_col}{row+1}:{last_monthly_col}{row+1})")
            self.write_to_sheet(row, col, formula_string, format_name="currency")

    def create_percent_change_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_start_col-3, "% Growth", format_name="grey_italic")
        for col in range(self.annual_start_col+1, self.annual_start_col+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_start_col+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                past_cell = get_cell_identifier(ref_row, col-1, absolute_row=True)
                present_cell = get_cell_identifier(ref_row, col, absolute_row=True)
                formula_string = f"=({present_cell}-{past_cell})/{past_cell}"
                
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")

    def create_monthly_referenced_line(self, row, ref_row, ref_col, ref_sheet_name):
        #This function populates a row with the contents of an entire row, essentially, repopulating the row across sheets.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.monthly_start_col
        col_offset = col - ref_col
        for year in range(1, self.num_forecasted_years+1):
            for month in range(1,13):
                #TODO: Automate which cells this pulls from
                formula_string = f"='{ref_sheet_name}'!{number_to_column_letter(col-col_offset)}${ref_row}"
                self.write_to_sheet(row, col, formula_string, format_name='currency_cross')
                col+=1
                
    def create_total_line(self, row, start_col, num_print_cols, num_sum_rows):
        #num_print_cols is the number of columns to apply the sum formula to
        for col in range(start_col, start_col+num_print_cols):
            formula_string = (f"=sum({number_to_column_letter(col)}${row-num_sum_rows}"
                              f":{number_to_column_letter(col)}${row})")
            self.write_to_sheet(row, col, formula_string, format_name="sum_line", print_formula=False)
    
    def write_to_sheet(self, row, col, formula_string, format_name="plain", print_formula=False):
        self.workbook_manager.validate_and_write(self.xlsxwriter_sheet, row, col, formula_string, format_name, print_formula)


    def populate_annual_monthly_headers(self, row, col):
        self.year_row=row #Save the row number for the row that years are listed
        #Annual headers
        self.write_to_sheet(row-1, self.annual_year0_start, 'Annual Pro Forma', format_name='bold')
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

    def create_percent_change_line(self, row, ref_row):
        self.write_to_sheet(row, self.annual_year0_start-3, "% Growth", format_name="grey_italic")
        for col in range(self.annual_year0_start+1, self.annual_year0_start+12*self.num_forecasted_years+self.gap_between_annual_and_monthly): #Start at col+1 since you can't get a percent change without two cells
            if col <self.annual_year0_start+self.num_forecasted_years or col>self.monthly_start_col: #Don't write to the intenionally blank columns
                past_cell = get_cell_identifier(ref_row, col-1, absolute_row=True)
                present_cell = get_cell_identifier(ref_row, col, absolute_row=True)
                formula_string = f"=({present_cell}-{past_cell})/{past_cell}"
                
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")
                
    def create_percent_margin_line(self, row, ref_row, add_annual=True, annual_only=False):
        self.write_to_sheet(row, self.annual_hist_start-2, "Margin (%)", format_name="grey_italic_right")
        
        if add_annual:
            range_start = self.annual_year0_start
        else:
            range_start = self.monthly_start_col
            
        if annual_only:
            range_end = self.annual_year0_start + self.num_forecasted_years
        else:
            range_end = self.monthly_start_col + 12*self.num_forecasted_years
            
        for col in range(range_start, range_end):
            if col < self.annual_year0_start + self.num_forecasted_years or (not annual_only and col > self.monthly_start_col - 1):
                formula_string = f"={get_cell_identifier(row-1,col)}/{get_cell_identifier(self.revenue_row,col, absolute_row=True)}"
                self.write_to_sheet(row, col, formula_string, format_name = "grey_percentage_italic")


    def create_monthly_from_single_cell(self, row, ref_row, ref_col, ref_sheet_name):
            col = self.monthly_start_col
            # Create an absolute reference to the source cell
            source_cell = f"='{ref_sheet_name}'!${number_to_column_letter(ref_col)}${ref_row}"
            
            # Use the same formula for all months
            for year in range(1, self.num_forecasted_years+1):
                for month in range(1,13):
                    self.write_to_sheet(row, col, source_cell, format_name='currency_cross')
                    col+=1

    def create_in_column_addition_subtraction(self, row, component_list, add_annual=True, annual_only=False):
        #The component list is a list of 2 items. The first one should always either be "+" or "-". The second one is the row being added or subtracted
        if add_annual:
            range_start = self.annual_year0_start
        else:
            range_start = self.monthly_start_col
            
        if annual_only:
            range_end = self.annual_year0_start + self.num_forecasted_years
        else:
            range_end = self.monthly_start_col + 12*self.num_forecasted_years
            
        for col in range(range_start, range_end):
            if col < self.annual_year0_start + self.num_forecasted_years or (not annual_only and col > self.monthly_start_col - 1):
                formula_string = "="
                for index, component in enumerate(component_list):
                    if index==0 and component == "+":
                        #Don't start equations with "+"
                        formula_string += get_cell_identifier(component[1], col, absolute_row=True)
                    else:
                        formula_string += component[0] + get_cell_identifier(component[1], col, absolute_row=True)
                self.write_to_sheet(row, col, formula_string, format_name="sum_line", print_formula=False)

    
    
    def create_monthly_same_sheet_line(self, row, ref_cell, ref_sheet_name):
            #This function writes each row. The consist of annual model and monthly models.
            #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
            col=self.monthly_start_col
            for year in range(1, self.num_forecasted_years+1):
                for month in range(1,13):
                    #TODO: Automate which cells this pulls from
                    formula_string = f"=${ref_cell}"
                    self.write_to_sheet(row, col, formula_string, format_name='currency', print_formula=False)
                    col+=1

    def create_annual_referenced_line(self, row, ref_row, ref_col, ref_sheet_name):
        #This function writes each row. The consist of annual model and monthly models.
        #ref_col and ref_row are the indicies of reference cell in the sheet that the referenced data comes from
        col=self.annual_year0_start
        col_offset = col - ref_col
        for year in range(1, self.num_forecasted_years+1):
            formula_string = f"='{ref_sheet_name}'!{number_to_column_letter(col-col_offset)}${ref_row}"
            self.write_to_sheet(row, col, formula_string, format_name='currency_cross', print_formula=False)
            col+=1

    def populate_annual_hist_data(self, row, line_name, format_name="plain"):
        for col in range(self.annual_hist_start, self.annual_year0_start):
            ref_year = str(self.business_object.start_year-self.annual_year0_start+col)
            if line_name in self.business_object.financials[ref_year]:
                self.write_to_sheet(row, col, self.business_object.financials[ref_year][line_name], format_name=format_name)
            else:
                #print(f"Error: {line_name} not in historical data.\n Keys are {self.business_object.financials[ref_year].keys()}")
                self.write_to_sheet(row, col, '', format_name=format_name) #Write nothing so at least the formatting stays