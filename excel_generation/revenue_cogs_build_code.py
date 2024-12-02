
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
        self.xlsxwriter_sheet.set_column('A:A', 5)   # Left margin column
        self.xlsxwriter_sheet.set_column('B:B', 35)  # Name column
        self.xlsxwriter_sheet.set_column('C:C', 15)  # Price column
        self.xlsxwriter_sheet.set_column('D:D', 12)  # Monthly transactions column
        self.xlsxwriter_sheet.set_column('E:E', 25)  # Total monthly revenue column
        self.xlsxwriter_sheet.set_column('F:F', 5)   # Spacer column
        self.xlsxwriter_sheet.set_column('G:G', 30)  # Price notes column
        self.xlsxwriter_sheet.set_column('H:H', 30)  # Frequency notes column
        self.xlsxwriter_sheet.set_column('I:I', 25)  # Price source column
        self.xlsxwriter_sheet.set_column('J:J', 25)  # Frequency source column
        self.xlsxwriter_sheet.set_column('K:K', 25)  # Additional spacing


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
     
        headers = ["Name", "Price", "Monthly Transactions", "Total Monthly Revenue", "", "Price Notes", "Frequency Notes", "Price Source", "Frequency Source"]
        for i, header in enumerate(headers):
            if header in ["Price", "Monthly Transactions", "Total Monthly Revenue"]:
                self.write_to_sheet(row, i+col, header, format_name="underline_right_wrap")
            else:
                self.write_to_sheet(row, i+col, header, format_name="underline")
        row += 1

        revenue_sources = self.business_object.revenue_sources
        for source in revenue_sources:
            # Write revenue source data in specified order
            self.write_to_sheet(row, col, source["revenue_source_name"])
            self.write_to_sheet(row, col+1, source["revenue_source_price"], format_name="currency_input") 
            self.write_to_sheet(row, col+2, source["monthly_transactions"], format_name="input")
            cell1 = get_cell_identifier(row,col+1, absolute_row=True)
            cell2 = get_cell_identifier(row,col+2, absolute_row=True)
            formula_string = f"={cell1}*{cell2}"
            self.write_to_sheet(row, col+3, formula_string, format_name="currency")
            self.write_to_sheet(row, col+5, source["price_notes"])  
            self.write_to_sheet(row, col+6, source["frequency_notes"])
            # Add price source as link
            self.write_to_sheet(row, col+7, f'=HYPERLINK("{source["price_source_link"]}", "{source["price_source"]}")', format_name='URL')
            # Add frequency source as link
            self.write_to_sheet(row, col+8, f'=HYPERLINK("{source["frequency_source_link"]}", "{source["frequency_source"]}")', format_name='URL')

            # Save reference to price cell for this revenue source
            self.cell_manager.add_cell_reference(self.sheet_name, source["revenue_source_name"],
                                               row=row, col=col+3)
            
            row += 1
        self.write_to_sheet(row, col+2, "Total", format_name="bold_right")
        self.write_to_sheet(row, col+3, f"=sum({number_to_column_letter(col+3)}${row-len(revenue_sources)+1}:{number_to_column_letter(col+3)}${row})", format_name="currency")
        self.cell_manager.add_cell_reference(self.sheet_name, "Total Revenue", row=row, col=col+4)
        row+=1
        
        # Add bottom border under revenue section
        for i in range(10):
            self.write_to_sheet(row, col+i, "", format_name="bottom_border")
        row += 2


        ##------ COGS section ------##
        self.write_to_sheet(row, col, "COGS Build", format_name='bold')
        row += 1

        headers = ["Name", "Cost", "Monthly Transactions", "Total Monthly Cost", "", "Cost Notes", "Frequency Notes", "Cost Source", "Frequency Source"]
        for i, header in enumerate(headers):
            if header in ["Cost", "Monthly Transactions", "Total Monthly Cost"]:
                self.write_to_sheet(row, i+col, header, format_name="underline_right_wrap")
            else:
                self.write_to_sheet(row, i+col, header, format_name="underline")
        row += 1

        for direct_cost in self.business_object.cost_of_sales_items:
            # Write cost item data
            self.write_to_sheet(row, col, direct_cost['cost_item_name'])
            self.write_to_sheet(row, col+1, direct_cost['cost_per_unit'], format_name="currency_input")
            self.write_to_sheet(row, col+2, direct_cost['monthly_transactions'], format_name="input")
            cell1 = get_cell_identifier(row,col+1, absolute_row=True)
            cell2 = get_cell_identifier(row,col+2, absolute_row=True)
            formula_string = f"={cell1}*{cell2}"
            self.write_to_sheet(row, col+3, formula_string, format_name="currency")
            self.write_to_sheet(row, col+5, direct_cost['cost_notes'])
            self.write_to_sheet(row, col+6, direct_cost['frequency_notes'])
            # Add cost source as link
            self.write_to_sheet(row, col+7, f'=HYPERLINK("{direct_cost["cost_source_link"]}", "{direct_cost["cost_source"]}")', format_name='URL')
            # Add frequency source as link
            self.write_to_sheet(row, col+8, f'=HYPERLINK("{direct_cost["frequency_source_link"]}", "{direct_cost["frequency_source"]}")', format_name='URL')

            # Save reference to cost per unit cell for this cost item
            self.cell_manager.add_cell_reference(self.sheet_name, direct_cost['cost_item_name'],
                                               row=row, col=col+3)

            row += 1
        self.write_to_sheet(row, col+2, "Total", format_name="bold_right")
        self.write_to_sheet(row, col+3, f"=sum({number_to_column_letter(col+3)}${row-len(revenue_sources)+1}:{number_to_column_letter(col+3)}${row})", format_name="currency")
        self.cell_manager.add_cell_reference(self.sheet_name, "Total COGS", row=row, col=col+4)
        row+=1
