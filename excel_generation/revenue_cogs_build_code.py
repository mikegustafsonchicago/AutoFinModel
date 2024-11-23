from helper_functions import number_to_column_letter, get_cell_identifier
import calendar
from datetime import datetime


class RevenueCogsBuildPage:
    def __init__(self, workbook_manager, cell_manager, business_object):
        self.workbook_manager = workbook_manager
        self.cell_manager = cell_manager
        self.business_object = business_object
        self.num_forecasted_years = self.workbook_manager.num_forecasted_years
        self.num_hist_years = len(self.business_object.hist_IS) if self.business_object.hist_IS else 0
        
        # Set start columns
        self.annual_hist_start = 3
        self.annual_year0_start = self.annual_hist_start + self.num_hist_years
        self.gap_between_annual_and_monthly = 1
        self.monthly_start_col = self.annual_year0_start + self.num_forecasted_years + self.gap_between_annual_and_monthly
        
        # Create the sheet
        self.sheet_name = 'Revenue COGS Build'
        self.sheet = self.workbook_manager.add_sheet(self.sheet_name)
        self.populate_sheet()

    def write_to_sheet(self, row, col, value, format_name='plain', print_formula=False, url_display=None):
        """Helper function to write to sheet using workbook manager"""
        self.workbook_manager.validate_and_write(self.sheet, row, col, value, format_name, print_formula, url_display)

    def populate_headers(self, row, col):
        """Populate the header row with years and months"""
        self.year_row = row
        # Annual headers
        self.write_to_sheet(row-1, self.annual_year0_start-self.num_hist_years, 'Historical', format_name='bold')
        self.write_to_sheet(row-1, self.annual_year0_start, 'Projected', format_name='bold')
        
        # Add historical years
        for i in range(self.num_hist_years):
            year = self.business_object.hist_IS[i]["year"]
            self.write_to_sheet(row, self.annual_hist_start + i, year, format_name='year_format')
            
        # Add projected years
        start_year_date = datetime(self.business_object.start_year, 1, 1)
        self.write_to_sheet(row, self.annual_year0_start, start_year_date, format_name='year_format')
        for col in range(self.annual_year0_start+1, self.annual_year0_start+self.num_forecasted_years):
            self.write_to_sheet(row, col, f"=edate({get_cell_identifier(row, col-1)},12)", format_name='year_format')

    def populate_sheet(self):
        """Main function to populate the entire sheet"""
        # Set column widths
        self.sheet.set_column('A:A', 5)
        self.sheet.set_column('B:B', 25)
        self.sheet.set_column('C:C', 10)
        self.sheet.set_column('D:D', 15)
        self.sheet.set_column('E:E', 12)
        self.sheet.set_column('F:F', 30)
        self.sheet.set_column('G:G', 10)

        # Page Title
        self.write_to_sheet(1, 1, 'Revenue and COGS Build', format_name="title")
        
        # Create the color banner row
        self.sheet.set_row(2, 5) # Make the row height smaller
        for col in range(1,10):
            self.write_to_sheet(2, col, "", format_name="color_banner")

        row = 5
        col = self.annual_hist_start

        # Add headers
        self.populate_headers(row, col)
        row += 2

        # Revenue section
        self.write_to_sheet(row, col-3, "Revenue Build", format_name='bold')
        row += 1
        
        # Revenue assumptions  
        self.write_to_sheet(row, col-3, "Revenue assumptions:", format_name='italic')
        row += 1
        
        # Add revenue metrics
        metrics = [
            "Average check per customer",
            "Store hours per day",
            "Days open per month", 
            "Customers per hour",
            "Total customers per month",
            "Growth rate in customer growth"
        ]
        
        for metric in metrics:
            self.write_to_sheet(row, col-3, metric)
            
            # Add historical data if available
            for i in range(self.num_hist_years):
                if metric == "Total customers per month":
                    # Calculate total customers from historical revenue
                    hist_revenue = self.business_object.hist_IS[i]["revenue"]
                    formula = f"={hist_revenue}/12/25" # Assuming $25 average check
                    self.write_to_sheet(row, self.annual_hist_start + i, formula, format_name='number')
                else:
                    self.write_to_sheet(row, self.annual_hist_start + i, "", format_name='number')
            row += 1

        # COGS section  
        self.write_to_sheet(row, col-3, "COGS Build", format_name='bold')
        row += 2

        # Save key row references for other sheets
        self.cell_manager.add_cell_reference(self.sheet_name, "Revenue", "Build", row=row, col=col)
