# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 14:59:33 2024

@author: mikeg
"""

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

# In helper_functions.py
class FormatManager:
    def __init__(self, workbook):
        self.formats = {
            'plain': workbook.add_format({'num_format': '@'} ), #No formatting
            'size_eight': workbook.add_format({'font_size': 8}), #Size 8 font
            'number': workbook.add_format({'num_format': '0'}), #Number format with no decimal places
            'currency': workbook.add_format({'num_format': '$#,##0'}),
            'currency_cents': workbook.add_format({'num_format': '$#,##0.00'}),
            'text_right_align' : workbook.add_format({'align': 'right'}),
            'percentage': workbook.add_format({'num_format': '0%'}),
            'decimal': workbook.add_format({'num_format': '0.000'}),
            'date': workbook.add_format({'num_format': 'mm/dd/yyyy'}),
            'bold': workbook.add_format({'bold': True}),
            'underline': workbook.add_format({'underline': True}),
            'underline_wrap': workbook.add_format({'underline': True,
                                                       'text_wrap': True}),
            'italic': workbook.add_format({'italic': True}),
            'top_border': workbook.add_format({'top': 1}),
            "bottom_border": workbook.add_format({'bottom': 1}),  # 1 indicates a thin border
            "bottom_border_wrap": workbook.add_format({'bottom': 1,
                                                       'text_wrap': True}),  # 1 indicates a thin border
            "color_banner": workbook.add_format({'bg_color': "484e41"}),  # 1 indicates a thin border
            "year_format" : workbook.add_format({'num_format': 'YYYY'}),
            "title": workbook.add_format({'bold': True, 
                                          'font_size': 14}),
            "sum_line": workbook.add_format({'top': 1, 
                                          'num_format': '$#,##0'}),
            "sum_line_cents": workbook.add_format({'top': 1, 
                                          'num_format': '$#,##0.00'}),
            "input": workbook.add_format({
                    'font_color': '0070C0',         # Text color (foreground)
                    'bg_color': 'FFFF66',           # Background color (fill)
                    'pattern': 1,                   # Required to enable background color
                }),
            "date_input_YYYY": workbook.add_format({
                    'font_color': '0070C0',         # Text color (foreground)
                    'bg_color': 'FFFF66',           # Background color (fill)
                    'pattern': 1,                   # Required to enable background color
                    'num_format': 'YYYY'      #Set the date format
                }),
            "percent_input": workbook.add_format({
                    'font_color': '0070C0',         # Text color (foreground)
                    'bg_color': 'FFFF66',           # Background color (fill)
                    'pattern': 1,                   # Required to enable background color
                    'num_format': '0%'
                }),
            "currency_input": workbook.add_format({
                     'num_format': '$#,##0',
                     'font_color': '0070C0',        # Text color (foreground)
                     'bg_color': 'FFFF66',          # Background color (fill)
                     'pattern': 1,              # Required to enable background color
                 }), 
            "currency_input_cents": workbook.add_format({
                     'num_format': '$#,##0.00',
                     'font_color': '0070C0',    # Text color (foreground)
                     'bg_color': 'FFFF66',   # Background color (fill)
                     'pattern': 1,            # Required to enable background color
                 }), 
            "cross_input": workbook.add_format({
                     'font_color': '006600',    # Text color (foreground)
                     'bg_color': 'e7ffcc',   # Background color (fill)
                     'pattern': 1,            # Required to enable background colorr
                     'right_color': '#bcd0a7',       # Orange right border color
                 }),
            "currency_cross": workbook.add_format({
                     'num_format': '$#,##0',
                     'font_color': '006600',    # Text color (foreground)
                     'bg_color': 'e7ffcc',   # Background color (fill)
                     'pattern': 1,          # Required to enable background color
                 }),
            "currency_cross_cents": workbook.add_format({
                     'num_format': '$#,##0.00',
                     'font_color': '006600',    # Text color (foreground)
                     'bg_color': 'e7ffcc',   # Background color (fill)
                     'pattern': 1          # Required to enable background color
                 }),
            "grey_italic": workbook.add_format({
                     'italic': True,
                     'font_color': '595959',    # Text color (foreground)
                }),
            "grey_italic_right": workbook.add_format({
                     'italic': True,
                     'font_color': '595959',    # Text color (foreground)
                     'align': 'right',
                }),
            "grey_percentage_italic": workbook.add_format({
                     'num_format': '0%',
                     'italic': True,
                     'font_color': '595959',    # Text color (foreground)
                }),
            "small_italic" : workbook.add_format({
                    'font_size': 8,
                    "italic":True
                }),
            "URL" : workbook.add_format({
                    'font_size': 11,  # Set the font size
                    'color': 'blue',  # Set the font color (optional)
                    'underline': 1    # Set underline (optional)
                }),
            "URL_small" : workbook.add_format({
                    'font_size': 8,  # Set the font size
                    'color': 'blue',  # Set the font color (optional)
                    'underline': 1    # Set underline (optional)
                })
        }

    def get_format(self, format_name):
        format_obj = self.formats.get(format_name, None)
        
        #error checking
        if isinstance(format_name, str) and ("=" in format_name or "*" in format_name):
            print(f"Error: Formula passed as format_name: {format_name}")
        if format_obj is None:
            # Diagnostic line to print or log a warning when a format is not found
            print(f"Warning: The format '{format_name}' does not exist in FormatManager.")
        return self.formats.get(format_name, None)
