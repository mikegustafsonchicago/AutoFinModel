def get_column_widths(excel_file):
    """
    Returns a dictionary of column widths for each worksheet in an Excel file.
    """
    import openpyxl
    
    # Load the workbook
    wb = openpyxl.load_workbook(excel_file)
    
    # Create dictionary to store widths
    sheet_widths = {}
    
    # Iterate through each worksheet
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        sheet_widths[sheet_name] = {}
        
        # Get column dimensions
        for col_letter, col_dimension in sheet.column_dimensions.items():
            width = col_dimension.width
            if width is not None:
                sheet_widths[sheet_name][col_letter] = width
                
    return sheet_widths

if __name__ == "__main__":
    # Example usage
    excel_file = "C:/Users/mikeg/OneDrive/Documents-Old/Random/auto_fin_model/Catalyst/CRC Two Page Summary.xlsx"
    widths = get_column_widths(excel_file)
    print(widths)
