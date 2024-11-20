# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 14:59:33 2024

@author: mikeg
"""
import yaml
import os

#Helper Functions
def number_to_column_letter(n):
    n+=1 #Converting indexing from xlsxwriter to excel
    """Convert a column number to an Excel-style column letter."""
    column_letter = ''
    while n > 0:
        n, remainder = divmod(n-1, 26)
        column_letter = chr(65 + remainder) + column_letter
    return column_letter

def get_cell_identifier(row, col, absolute_row=False, absolute_col=False):
    """Convert a (row, column) tuple to an Excel-style cell identifier, optionally making row and/or column absolute."""
    column_letter = number_to_column_letter(col)  # Convert the column number to a letter
    row_number = row + 1  # Convert to 1-based index for Excel
    col_prefix = '$' if absolute_col else ''  # Add $ for absolute column reference
    row_prefix = '$' if absolute_row else ''  # Add $ for absolute row reference
    return f"{col_prefix}{column_letter}{row_prefix}{row_number}"

def create_total_line(workbook_manager, sheet, row, start_col, num_print_cols, num_sum_rows):
    #num_print_cols is the number of columns to apply the sum formula to
    for col in range(start_col, start_col+num_print_cols):
        formula_string = (f"=sum({number_to_column_letter(col)}${row-num_sum_rows}"
                          f":{number_to_column_letter(col)}${row})")
        workbook_manager.validate_and_write(sheet, row, col, formula_string, format_name="sum_line", print_formula=False)



class FormatManager:
    def __init__(self, workbook, config_file='standard.yaml'):
        
        # Get the path to the 'formats' folder
        self.base_dir = os.path.dirname(__file__)
        self.formats_folder = os.path.join(self.base_dir, 'formats')
        self.config_path = os.path.join(self.formats_folder, config_file)

        self.workbook = workbook
        self.formats = {}
        self._load_formats_from_yaml(config_file)

    def _load_formats_from_yaml(self, config_file):
        # Load format configurations from the YAML file
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Create formats dynamically based on the YAML configuration
        for format_name, format_properties in config.items():
            self.formats[format_name] = self.workbook.add_format(format_properties)

    def get_format(self, format_name):
        format_obj = self.formats.get(format_name, None)
        
        # Error checking
        if isinstance(format_name, str) and ("=" in format_name or "*" in format_name):
            print(f"Error: Formula passed as format_name: {format_name}")
        if format_obj is None:
            # Diagnostic line to print or log a warning when a format is not found
            print(f"Warning: The format '{format_name}' does not exist in FormatManager.")
        
        return format_obj


