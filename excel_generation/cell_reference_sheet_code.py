from workbook_sheet_manager_code import SheetManager

class CellReferenceDebugPage(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
        
        self.populate_sheet()

    def populate_sheet(self):
        """Main function to populate the entire sheet"""
        # Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5)   # Margin column
        self.xlsxwriter_sheet.set_column('B:B', 30)  # Sheet name
        self.xlsxwriter_sheet.set_column('C:C', 30)  # Key path
        self.xlsxwriter_sheet.set_column('D:D', 15)  # Row
        self.xlsxwriter_sheet.set_column('E:E', 15)  # Column
        self.xlsxwriter_sheet.set_column('F:F', 15)  # Cell Reference

        # Page Title
        self.write_to_sheet(1, 1, 'Cell Reference Debug Page', format_name="title")
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5)
        for col in range(1,7):
            self.write_to_sheet(2, col, "", format_name="color_banner")

        # Headers
        row = 4
        col = 1
        headers = ["Sheet", "Key Path", "Row", "Column", "Cell Reference"]
        for i, header in enumerate(headers):
            self.write_to_sheet(row, i+col, header, format_name="underline")
        
        row += 1
        
        # Iterate through all cell references
        for sheet_name, sheet_data in self.cell_manager.cell_references.items():
            def print_references(data, current_path=""):
                nonlocal row
                if isinstance(data, tuple):  # Base case - actual cell reference
                    cell_row, cell_col = data
                    cell_ref = self.cell_manager.row_col_to_cell_ref(cell_row, cell_col)
                    
                    self.write_to_sheet(row, col, sheet_name)
                    self.write_to_sheet(row, col+1, current_path)
                    self.write_to_sheet(row, col+2, cell_row)
                    self.write_to_sheet(row, col+3, cell_col)
                    self.write_to_sheet(row, col+4, cell_ref)
                    
                    row += 1
                else:  # Recursive case - dictionary
                    for key, value in data.items():
                        new_path = f"{current_path} -> {key}" if current_path else key
                        print_references(value, new_path)
            
            print_references(sheet_data)
