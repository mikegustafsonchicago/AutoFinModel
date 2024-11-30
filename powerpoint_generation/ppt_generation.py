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

def get_color(hex_code):
    """Convert hex color to RGB tuple."""
    hex_code = hex_code.lstrip('#')
    return int(hex_code[:2], 16), int(hex_code[2:4], 16), int(hex_code[4:], 16)

def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def generate_ppt():
    # Move all the file path definitions and main logic inside this function
    current_directory = os.getcwd()
    file_name = "output_ppt.pptx"
    data_path = "temp_business_data"
    output_path = os.path.join(current_directory, "outputs", file_name)
    data_path = os.path.join(current_directory, data_path)
    
    # Define file paths
    employees_file = os.path.join(data_path, 'employees.json')
    revenue_file = os.path.join(data_path, 'revenue_build.json')
    cost_of_sales_file = os.path.join(data_path, 'cost_of_sales.json')
    operating_expenses_file = os.path.join(data_path, 'OPEX.json')
    capex_file = os.path.join(data_path, 'CAPEX.json')
    
    yaml_file = os.path.join(current_directory, "excel_generation/formats/", 'standard.yaml')

    # Load YAML for styling
    with open(yaml_file, 'r') as file:
        styles = yaml.safe_load(file)

    # Load all JSON data with error handling
    try:
        employees = load_json(employees_file) if os.path.exists(employees_file) else []
        revenue = load_json(revenue_file) if os.path.exists(revenue_file) else []
        cost_of_sales = load_json(cost_of_sales_file) if os.path.exists(cost_of_sales_file) else []
        operating_expenses = load_json(operating_expenses_file) if os.path.exists(operating_expenses_file) else [] 
        capex = load_json(capex_file) if os.path.exists(capex_file) else []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error loading JSON files: {str(e)}")
        raise

    # Create PowerPoint presentation
    presentation = Presentation()
    # Title slide
    title_slide = presentation.slides.add_slide(presentation.slide_layouts[0])  # Use layout 0 for title slide
    title = title_slide.placeholders[0]  # Get title placeholder
    title.text = "Financial Model"

    # Slide 2: Revenue Sources 
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])  # Layout 1 has a title
    title = slide.shapes.title
    title.text = "Revenue Sources"

    # Create table for revenue sources
    rows = len(revenue["revenue_sources"]) + 1
    cols = 3

    table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table

    # Set headers
    headers = ["Revenue Stream", "Price", "Monthly Transactions"]
    for i, header in enumerate(headers):
        table.cell(0, i).text = header
        header_font = table.cell(0, i).text_frame.paragraphs[0].font
        header_font.bold = True
        header_font.size = Pt(14)
        header_font.color.rgb = RGBColor(255, 255, 255)

    # Populate revenue data
    for i, source in enumerate(revenue["revenue_sources"]):
        table.cell(i + 1, 0).text = source["revenue_source_name"]
        table.cell(i + 1, 1).text = f"${source['revenue_source_price']}"
        table.cell(i + 1, 2).text = str(source["monthly_transactions"])

    # Slide 2: Operating Expenses
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    title = slide.shapes.title
    title.text = "Operating Expenses"

    # Create table for operating expenses
    rows = len(operating_expenses["expenses"]) + 1
    cols = 3

    table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(3)).table

    # Set headers
    headers = ["Expense Name", "Amount", "Frequency"]
    for i, header in enumerate(headers):
        table.cell(0, i).text = header
        header_font = table.cell(0, i).text_frame.paragraphs[0].font
        header_font.bold = True
        header_font.size = Pt(14)
        header_font.color.rgb = RGBColor(255, 255, 255)

    # Populate expense data
    for i, expense in enumerate(operating_expenses["expenses"]):
        table.cell(i + 1, 0).text = expense["expense_name"]
        table.cell(i + 1, 1).text = f"${expense['amount']}"
        table.cell(i + 1, 2).text = expense["frequency"]

    # Slide 3: Capital Expenditures
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    title = slide.shapes.title
    title.text = "Capital Expenditures"
    content = slide.placeholders[1]
    
    for expense in capex["expenses"]:
        content.text += (
            f"\n{expense['expense_name']}: ${expense['amount']} "
            f"(Purchased {expense['purchase_year']}, {expense['depreciation_life']} year depreciation)"
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

if __name__ == "__main__":
    generate_ppt()