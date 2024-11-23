# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 10:05:30 2024

@author: mikeg
"""
import re

class CellManager:
    def __init__(self):
        # Stores references in a multi-tiered dictionary structure
        # Allows for arbitrary tiers (e.g., sheet -> recipe -> component -> row/col)
        self.cell_references = {}

    # Helper method to convert an Excel cell reference (e.g., 'A1') to (row, column) pair
    def cell_ref_to_row_col(self, cell_ref):
        match = re.match(r"([A-Za-z]+)([0-9]+)", cell_ref)
        if not match:
            raise ValueError(f"Invalid cell reference format: {cell_ref}")
        column_letters, row = match.groups()
        row = int(row)
        column = self.column_letter_to_index(column_letters)
        return row, column

    # Helper method to convert (row, column) to Excel-style cell reference
    def row_col_to_cell_ref(self, row, col, absolute_row=False, absolute_col=False):
        """Convert (row, column) to Excel-style cell reference, with optional absolute row/col."""
        column_letter = self.index_to_column_letter(col)
        row_number = row
        col_prefix = '$' if absolute_col else ''
        row_prefix = '$' if absolute_row else ''
        return f"{col_prefix}{column_letter}{row_prefix}{row_number}"

    # Convert Excel column letter (e.g., 'A') to a column index (e.g., 1 for 'A')
    def column_letter_to_index(self, column_letters):
        index = 0
        for letter in column_letters.upper():
            index = index * 26 + (ord(letter) - ord('A') + 1)
        return index

    # Convert a column index to an Excel column letter (e.g., 1 to 'A')
    def index_to_column_letter(self, index):
        result = ''
        while index > 0:
            index -= 1
            result = chr(index % 26 + ord('A')) + result
            index //= 26
        return result

    # Recursive method to navigate the dictionary and add the reference at the correct tier
    def _add_reference_recursive(self, current_level, keys, row, col):
        if len(keys) == 1:
            # Base case: final tier, store the row/col
            current_level[keys[0]] = (row, col)
        else:
            # Recursive case: create a new dictionary level if needed
            if keys[0] not in current_level:
                current_level[keys[0]] = {}
            self._add_reference_recursive(current_level[keys[0]], keys[1:], row, col)

    # Method to add a new cell reference with any number of tiers
    def add_cell_reference(self, *keys, row=None, col=None, cell_ref=None):
        """
        Add a new cell reference dynamically with any number of tiers (e.g., sheet -> recipe -> component).
        - keys: sequence of keys representing the hierarchy (e.g., sheet, recipe, component)
        - Input either (row, col) or cell_ref (e.g., 'A1')
        """
        if cell_ref:
            row, col = self.cell_ref_to_row_col(cell_ref)
        elif row is None or col is None:
            raise ValueError("Must provide either (row, col) or cell_ref")
        #---IMPORTANT----#
        #The 2 lines below are what convert indexing. xlsxwriter starts at 0, but excel starts at 1. So 0,0 needs to become A1.
        row+=1
        col+=1
        #-----------
        self._add_reference_recursive(self.cell_references, keys, row, col)
    
    # Recursive method to navigate the dictionary and retrieve the reference at the correct tier
    def _get_reference_recursive(self, current_level, keys):
        if len(keys) == 1:
            if keys[0] in current_level:
                return current_level[keys[0]]
            else:
                raise KeyError(f"Key {keys[0]} not found")
        else:
            if keys[0] in current_level:
                return self._get_reference_recursive(current_level[keys[0]], keys[1:])
            else:
                raise KeyError(f"Key {keys[0]} not found")

    # Method to retrieve a cell reference with any number of tiers
    def get_cell_reference(self, *keys, format_type='cell_ref', absolute_row=False, absolute_col=False):
        """
        Retrieves the cell reference with any number of tiers (e.g., sheet -> recipe -> component).
        format_type:
        - 'cell_ref': returns Excel-style reference (e.g., 'A1')
        - 'row': returns row number
        - 'col': returns column number
        """
        # Validate format type before proceeding
        valid_formats = ['cell_ref', 'row', 'col']
        if format_type not in valid_formats:
            raise ValueError(f"Invalid format_type: '{format_type}'. Must be one of: {valid_formats}")

         # Validate that keys were provided
        if not keys:
            raise ValueError("No keys provided. Must provide at least one key (e.g., sheet name)")

        try:
            row, col = self._get_reference_recursive(self.cell_references, keys)
        except KeyError as e:
            # Build helpful error message showing available keys at each level
            current_dict = self.cell_references
            available_path = []
            requested_path = []
            
            for i, key in enumerate(keys):
                requested_path.append(key)
                if key in current_dict:
                    available_path.append(key)
                    current_dict = current_dict[key]
                else:
                    available_keys = list(current_dict.keys())
                    raise KeyError(
                        f"\nRequested path: {' -> '.join(requested_path)}\n"
                        f"Available path: {' -> '.join(available_path)}\n"
                        f"Key '{key}' not found at level {i+1}.\n"
                        f"Available keys at this level: {available_keys}"
                    )

        try:
            if format_type == 'cell_ref':
                return self.row_col_to_cell_ref(row, col, absolute_row=absolute_row, absolute_col=absolute_col)
            elif format_type == 'row':
                return row
            else:  # format_type == 'col'
                return col-1  # Adjust for indexing mismatch when returning column
        except Exception as e:
            raise Exception(f"Error processing cell reference for {' -> '.join(keys)}: {str(e)}")


# Data Structure Description:

# The cell_references attribute is a multi-tier dictionary that allows for storing cell references in a hierarchical format.
# You can define as many levels of hierarchy as needed. Each level corresponds to a key in the dictionary.

# Example of a cell_references structure:
# cell_references = {
#     'Recipes': {                      # The sheet or high-level category
#         'Large Black Coffee': {        # A recipe or mid-level category
#             'Coffee': (5, 2),          # A component within the recipe (row 5, column 2)
#             'Water': (6, 3)            # Another component (row 6, column 3)
#         },
#         'Cappuccino': {                # Another recipe
#             'Milk': {
#                 'Steamed': (7, 4)      # Nested component (row 7, column 4)
#             }
#         }
#     }
# }

# This structure allows for:
# - Organizing cell references by sheets, recipes, components, or any other hierarchical levels.
# - Flexible, dynamic addition of references.
# - Easy retrieval of specific cell references based on hierarchical keys.

# ---------------------------------------
# Example Usage (commented out):
#
# # Adding using sheet -> recipe -> ingredient/component hierarchy
# cell_manager.add_cell_reference('Recipes', 'Large Black Coffee', 'Coffee', cell_ref='B3')
# cell_manager.add_cell_reference('Recipes', 'Large Black Coffee', 'Water', row=4, col=3)
#
# # Adding using more tiers (e.g., for detailed recipes)
# cell_manager.add_cell_reference('Recipes', 'Cappuccino', 'Milk', 'Steamed', cell_ref='C5')
#
# # Retrieving in different formats
# print(cell_manager.get_cell_reference('Recipes', 'Large Black Coffee', 'Coffee', format_type='cell_ref'))  # Outputs: 'B3'
# print(cell_manager.get_cell_reference('Recipes', 'Large Black Coffee', 'Water', format_type='row'))         # Outputs: 4
# print(cell_manager.get_cell_reference('Recipes', 'Cappuccino', 'Milk', 'Steamed', format_type='col'))       # Outputs: 3
# ---------------------------------------
