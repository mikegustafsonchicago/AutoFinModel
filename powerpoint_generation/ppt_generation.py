# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 13:00:59 2024

@author: mikeg
"""
import os
import json
import yaml
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor


# Paths to your files
current_directory = os.getcwd()
file_name = "output_ppt.pptx"
parent_directory = os.path.dirname(current_directory)
data_path = "temp_business_data"
output_path = os.path.join(current_directory, file_name)
data_path = os.path.join(parent_directory, data_path)
fundamentals_file = os.path.join(data_path, 'fundamentals.json')
hist_IS_file = os.path.join(data_path, 'hist_IS.json')
investment_team_file = os.path.join(data_path, 'investment_team.json')
CAPEX_file = os.path.join(data_path, 'CAPEX.json')
comparables_file = os.path.join(data_path, 'employees.json')
employees_file = os.path.join(data_path, 'employees.json')
fees_key_terms_file = os.path.join(data_path, 'fees_key_terms.json')
financials_file = os.path.join(data_path, 'financials.json')

yaml_file = os.path.join(parent_directory,"excel_generation/formats/", 'catalystPartners.yaml')

# Load YAML for styling
with open(yaml_file, 'r') as file:
    styles = yaml.safe_load(file)

# Utility functions for styling
def get_color(hex_code):
    """Convert hex color to RGB tuple."""
    hex_code = hex_code.lstrip('#')
    return int(hex_code[:2], 16), int(hex_code[2:4], 16), int(hex_code[4:], 16)

# Load data from JSON files
def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

fundamentals = load_json(fundamentals_file)
hist_IS = load_json(hist_IS_file)

investment_team = load_json(investment_team_file)
CAPEX = load_json(CAPEX_file)
comparables = load_json(comparables_file)
employees = load_json(employees_file)
fees_key_terms = load_json(fees_key_terms_file)
financials = load_json(financials_file)

# Create PowerPoint presentation
presentation = Presentation()

# Add slides
# Slide 1: Fundamentals
slide = presentation.slides.add_slide(presentation.slide_layouts[0])
title = slide.shapes.title
title.text = "Firm Fundamentals"
content = slide.placeholders[1]
content.text = (
    f"Firm Name: {fundamentals[0]['firm_name']}\n"
    f"Founded: {fundamentals[0]['founded_year']}\n"
    f"Primary Office: {fundamentals[0]['primary_office']}\n"
    f"Website: {fundamentals[0]['website']}"
)

# Access Slide 1
slide = presentation.slides[0]

# Style the Title
title = slide.shapes.title
title.text_frame.paragraphs[0].font.name = "Times New Roman"  # From the 'title' style
title.text_frame.paragraphs[0].font.size = Pt(48)
r, g, b = int('0F', 16), int('27', 16), int('49', 16)  # Hex color '#0F2749'
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(r, g, b)

# Add Background Color
slide_background = slide.background
fill = slide_background.fill
fill.solid()
r, g, b = int('48', 16), int('4e', 16), int('41', 16)  # Hex color '#484e41'
fill.fore_color.rgb = RGBColor(r, g, b)

# Style Content Text
content = slide.placeholders[1]
for paragraph in content.text_frame.paragraphs:
    for run in paragraph.runs:
        run.font.name = "Arial"  # From 'plain'
        run.font.size = Pt(14)
        r, g, b = int('59', 16), int('59', 16), int('59', 16)  # Hex color '#595959'
        run.font.color.rgb = RGBColor(r, g, b)
        run.font.italic = True  # From 'grey_italic'

# Add Extra Decorative Text
textbox = slide.shapes.add_textbox(Inches(0.5), Inches(4), Inches(8), Inches(0.5))
textbox_frame = textbox.text_frame
textbox_frame.text = "Decorative Footer Example"
textbox_paragraph = textbox_frame.paragraphs[0]
textbox_paragraph.font.name = "Arial"
textbox_paragraph.font.size = Pt(18)
textbox_paragraph.font.bold = True
textbox_paragraph.font.underline = True  # From 'bold_underline'
textbox_paragraph.font.color.rgb = RGBColor(0, 112, 192)  # From 'input'



# Slide 2: Historical Income Statement
slide = presentation.slides.add_slide(presentation.slide_layouts[1])
title = slide.shapes.title
title.text = "Historical Income Statement"


# Access Slide 2
slide = presentation.slides[1]

# Extract historical financial data
years = [year_data["year"] for year_data in hist_IS["historical_financials"]]
metrics = ["Revenue", "Net Income"]

# Define table dimensions
rows = len(metrics) + 1  # +1 for the metric headers
cols = len(years) + 1  # +1 for the first column (metrics)

# Add a table to the slide
table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table

# Set the first row as column headers (Years)
table.cell(0, 0).text = ""  # Empty corner cell
for i, year in enumerate(years):
    table.cell(0, i + 1).text = str(year)
    header_font = table.cell(0, i + 1).text_frame.paragraphs[0].font
    header_font.bold = True
    header_font.underline = True
    header_font.size = Pt(14)
    header_font.color.rgb = RGBColor(0, 0, 0)  # White color

# Set the first column as row headers (Metrics)
for i, metric in enumerate(metrics):
    table.cell(i + 1, 0).text = metric
    row_header_font = table.cell(i + 1, 0).text_frame.paragraphs[0].font
    row_header_font.bold = True
    row_header_font.size = Pt(14)
    row_header_font.color.rgb = RGBColor(0, 0, 0)  # White color

# Populate the table with financial data
for i, metric in enumerate(metrics):
    for j, year_data in enumerate(hist_IS["historical_financials"]):
        value = year_data["revenue"] if metric == "Revenue" else year_data["net_income"]
        table.cell(i + 1, j + 1).text = f"${value}M"
        content_font = table.cell(i + 1, j + 1).text_frame.paragraphs[0].font
        content_font.size = Pt(12)
        content_font.name = "Arial"
        content_font.color.rgb = RGBColor(0, 0, 0)  # Black color

# Style the table headers with background colors
for i in range(cols):
    header_cell = table.cell(0, i)
    fill = header_cell.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(255, 255, 255)  # Dark blue background for headers

for i in range(rows - 1):
    row_header_cell = table.cell(i + 1, 0)
    fill = row_header_cell.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(255, 255, 255)  # Dark blue background for row headers
    

# Slide 3: Investment Team
slide = presentation.slides.add_slide(presentation.slide_layouts[1])
title = slide.shapes.title
title.text = "Investment Team"

# Access Slide 3
slide = presentation.slides[2]

# Define the number of rows and columns for the table
rows = len(investment_team["members"]) + 1  # +1 for the header
cols = 2

# Add a table to the slide
table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(3)).table

# Set column headers
table.cell(0, 0).text = "Name"
table.cell(0, 1).text = "Title"

# Apply header styling
header_font = table.cell(0, 0).text_frame.paragraphs[0].font
header_font.bold = True
header_font.size = Pt(14)
header_font.color.rgb = RGBColor(255, 255, 255)  # White color

header_font = table.cell(0, 1).text_frame.paragraphs[0].font
header_font.bold = True
header_font.size = Pt(14)
header_font.color.rgb = RGBColor(255, 255, 255)  # White color

# Set header background color
for col in range(cols):
    cell = table.cell(0, col)
    fill = cell.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(15, 39, 73)  # Hex: #0F2749

# Populate the table with investment team members
for i, member in enumerate(investment_team["members"]):
    table.cell(i + 1, 0).text = member["investment_team_member_name"]
    table.cell(i + 1, 1).text = member["investment_team_member_title"]

    # Apply content styling
    for j in range(cols):
        content_font = table.cell(i + 1, j).text_frame.paragraphs[0].font
        content_font.size = Pt(12)
        content_font.name = "Arial"
        content_font.color.rgb = RGBColor(89, 89, 89)  # Hex: #595959 (gray)

# Slide 4: CAPEX Overview
slide = presentation.slides.add_slide(presentation.slide_layouts[1])
title = slide.shapes.title
title.text = "CAPEX Overview"
content = slide.placeholders[1]
for expense in CAPEX["expenses"]:
    content.text += (
        f"\n{expense['expense_name']}: ${expense['amount']} ({expense['purchase_year']})"
    )



# Apply styles from YAML
def apply_styles(presentation, styles):
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(styles.get('font_size', 18))
                        if 'font_color' in styles:
                            r, g, b = get_color(styles['font_color'])
                            run.font.color.rgb = RGBColor(r, g, b)

apply_styles(presentation, styles)

# Save PowerPoint
presentation.save(output_path)
print(f"Presentation saved to {output_path}")
