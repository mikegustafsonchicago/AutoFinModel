
import calendar
from datetime import datetime
from workbook_sheet_manager_code import SheetManager
from helper_functions import number_to_column_letter, get_cell_identifier

class RevenueCogsBuildPage(SheetManager):
    def __init__(self, workbook_manager, business_object, sheet_name):
        super().__init__(workbook_manager, business_object, sheet_name)
        self.num_forecasted_years = self.workbook_manager.num_forecasted_years
        self.num_hist_years = len(self.business_object.hist_IS) if self.business_object.hist_IS else 0
        
        # Set start columns
        self.annual_hist_start = 7
        self.annual_year0_start = self.annual_hist_start + self.num_hist_years
        self.gap_between_annual_and_monthly = 1
        self.monthly_start_col = self.annual_year0_start + self.num_forecasted_years + self.gap_between_annual_and_monthly
        
        self.populate_sheet()

    def populate_sheet(self):
        """Main function to populate the entire sheet"""
        # Set column widths
        self.xlsxwriter_sheet.set_column('A:A', 5)   # Margin column
        self.xlsxwriter_sheet.set_column('B:B', 35)  # Revenue source name
        self.xlsxwriter_sheet.set_column('C:C', 15)  # Price
        self.xlsxwriter_sheet.set_column('D:D', 12)  # Frequency
        self.xlsxwriter_sheet.set_column('E:E', 25)  # Frequency notes
        self.xlsxwriter_sheet.set_column('F:F', 25)  # Price source
        self.xlsxwriter_sheet.set_column('G:G', 10)  # Frequency source
        self.xlsxwriter_sheet.set_column('H:H', 20)  # Historical data start
        self.xlsxwriter_sheet.set_column('I:I', 20)  # Historical and projected years


        # Page Title
        self.write_to_sheet(1, 1, 'Revenue and COGS Build', format_name="title")
        
        # Create the color banner row
        self.xlsxwriter_sheet.set_row(2, 5) # Make the row height smaller
        for col in range(1,10):
            self.write_to_sheet(2, col, "", format_name="color_banner")

        row = 5
        col = 1

        ##------ Revenue section ------##
        self.write_to_sheet(row, col, "Revenue Build", format_name='bold')
        row += 1        
     
        headers = ["Name", "Price", "Monthly Transactions", "Frequency Notes", "Total Monthly Revenue", "", "Price Source", "Frequency Source"]
        for i, header in enumerate(headers):
            self.write_to_sheet(row, i+col, header, format_name="underline")
        row += 1

        revenue_sources = self.business_object.revenue_sources
        for source in revenue_sources:
            # Write revenue source data in specified order
            self.write_to_sheet(row, col, source["revenue_source_name"])
            self.write_to_sheet(row, col+1, source["revenue_source_price"], format_name="currency_cents") 
            self.write_to_sheet(row, col+2, source["monthly_transactions"], format_name="number")
            self.write_to_sheet(row, col+3, source["frequency_notes"])
            cell1 = get_cell_identifier(row,col+1, absolute_row=True)
            cell2 = get_cell_identifier(row,col+2, absolute_row=True)
            formula_string = f"={cell1}*{cell2}"
            self.write_to_sheet(row, col+4, formula_string, format_name="currency")
            # Add price source as link
            self.write_to_sheet(row, col+6, f'=HYPERLINK("{source["price_source_link"]}", "{source["price_source"]}")', format_name='URL')
            # Add frequency source as link
            self.write_to_sheet(row, col+7, f'=HYPERLINK("{source["frequency_source_link"]}", "{source["frequency_source"]}")', format_name='URL')

            # Save reference to price cell for this revenue source
            self.cell_manager.add_cell_reference(self.sheet_name, source["revenue_source_name"],
                                               row=row, col=col+4)
            
            row += 1
        self.write_to_sheet(row, col+3, "Total")
        self.write_to_sheet(row, col+4, f"=sum({number_to_column_letter(col+4)}${row-len(revenue_sources)+1}:{number_to_column_letter(col+4)}${row})", format_name="currency")
        self.cell_manager.add_cell_reference(self.sheet_name, "Total Revenue", row=row, col=col+4)
        row+=1
        
        # Add bottom border under revenue section
        for i in range(10):
            self.write_to_sheet(row, col+i, "", format_name="bottom_border")
        row += 2


        ##------ COGS section ------##
        self.write_to_sheet(row, col, "COGS Build", format_name='bold')
        row += 1

        # Add headers
        headers = ["Name", "Cost", "Monthly Transactions", "Frequency Notes", "Total Monthly Cost","", "Cost Source", "Frequency Source"]
        for i, header in enumerate(headers):
            self.write_to_sheet(row, i+col, header, format_name="underline")
        row += 1

        for direct_cost in self.business_object.cost_of_sales_items:
            # Write cost item data
            self.write_to_sheet(row, col, direct_cost['cost_item_name'])
            self.write_to_sheet(row, col+1, direct_cost['cost_per_unit'], format_name="currency_cents")
            self.write_to_sheet(row, col+2, direct_cost['monthly_transactions'], format_name="number")
            self.write_to_sheet(row, col+3, direct_cost['frequency_notes'])
            cell1 = get_cell_identifier(row,col+1, absolute_row=True)
            cell2 = get_cell_identifier(row,col+2, absolute_row=True)
            formula_string = f"={cell1}*{cell2}"
            self.write_to_sheet(row, col+4, formula_string, format_name="currency")
            # Add cost source as link
            self.write_to_sheet(row, col+6, f'=HYPERLINK("{direct_cost["cost_source_link"]}", "{direct_cost["cost_source"]}")', format_name='URL')
            # Add frequency source as link
            self.write_to_sheet(row, col+7, f'=HYPERLINK("{direct_cost["frequency_source_link"]}", "{direct_cost["frequency_source"]}")', format_name='URL')

            # Save reference to cost per unit cell for this cost item
            self.cell_manager.add_cell_reference(self.sheet_name, direct_cost['cost_item_name'],
                                               row=row, col=col+4)

            row += 1
        self.write_to_sheet(row, col+3, "Total")
        self.write_to_sheet(row, col+4, f"=sum({number_to_column_letter(col+4)}${row-len(revenue_sources)+1}:{number_to_column_letter(col+4)}${row})", format_name="currency")
        self.cell_manager.add_cell_reference(self.sheet_name, "Total COGS", row=row, col=col+4)
        row+=1
