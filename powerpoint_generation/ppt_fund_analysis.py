# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 13:00:59 2024

@author: mikeg

This module handles PowerPoint presentation generation for financial analysis.
It creates slides for revenue sources, costs, employees, expenses and capital expenditures.

Key components:
- Utility functions for styling and color handling
- Main presentation generation function
- Individual slide generation for each financial aspect
"""

#------------------------------------------------------------------------------
# Imports and Setup
#------------------------------------------------------------------------------
import os
import json
import yaml
import logging
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.dml.color import MSO_THEME_COLOR
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'excel_generation'))
from business_entity_code import BusinessEntity
from io import BytesIO

#------------------------------------------------------------------------------
# Utility Functions
#------------------------------------------------------------------------------
def get_color(hex_code):
    """
    Convert hex color code to RGB tuple.
    
    Args:
        hex_code (str): Hex color code (e.g. '#FF0000')
    Returns:
        tuple: RGB values as (r,g,b)
    """
    hex_code = hex_code.lstrip('#')
    return int(hex_code[:2], 16), int(hex_code[2:4], 16), int(hex_code[4:], 16)

def load_json(filepath):
    """Load and parse JSON file."""
    with open(filepath, 'r') as file:
        return json.load(file)

def apply_table_styles(table, header_font_size=14):
    """
    Apply consistent styling to PowerPoint table headers and cells.
    Uses black and white table style.
    
    Args:
        table: PowerPoint table object
        header_font_size (int): Font size for header row
    """
    # Apply black and white table style
    table.style = 'Table Grid'
    
    # Style headers
    for cell in table.rows[0].cells:
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0, 0, 0)
        paragraph = cell.text_frame.paragraphs[0]
        paragraph.font.bold = True
        paragraph.font.size = Pt(header_font_size)
        paragraph.font.color.rgb = RGBColor(255, 255, 255)
    
    # Style data cells with alternating shading
    for i in range(1, len(table.rows)):
        for cell in table.rows[i].cells:
            cell.fill.solid()
            # Alternate between white and light gray
            if i % 2 == 0:
                cell.fill.fore_color.rgb = RGBColor(255, 255, 255)
            else:
                cell.fill.fore_color.rgb = RGBColor(242, 242, 242)
            paragraph = cell.text_frame.paragraphs[0]
            paragraph.font.size = Pt(12)
            paragraph.font.color.rgb = RGBColor(0, 0, 0)

#------------------------------------------------------------------------------
# Main Presentation Generation
#------------------------------------------------------------------------------
def generate_fund_analysis_ppt():
    """Generate a PowerPoint presentation for fund analysis"""
    from io import BytesIO
    
    # Create your PowerPoint
    prs = Presentation()
    
    # Load data using BusinessEntity
    try:
        business = BusinessEntity("fund_analysis")
        fundamentals = business.fundamentals
        investment_team = business.investment_team
        seed_terms = business.seed_terms
        fees_key_terms = business.fees_key_terms
        deal_history = business.deal_history
        service_providers = business.service_providers
    except Exception as e:
        logging.error(f"Error loading fund data: {str(e)}")
        raise

    #--- 1 --- Title Slide ---
    try:
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        title.text = "Fund Analysis Overview"
        subtitle.text = "Investment Strategy and Performance"
    except Exception as e:
        logging.error(f"Error creating title slide: {str(e)}")

    #--- 2 --- Fund Fundamentals Slide ---
    try:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        title = slide.shapes.title
        title.text = "Fund Fundamentals"
        
        # Get the first fundamentals entry
        fund_data = fundamentals[0]
        
        rows = len(fund_data) + 1
        cols = 2
        table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table
        
        headers = ["Metric", "Value"]
        for i, header in enumerate(headers):
            table.cell(0, i).text = header
            
        for i, (key, value) in enumerate(fund_data.items(), 1):
            if key not in ['source', 'source_notes']:
                table.cell(i, 0).text = key.replace('_', ' ').title()
                table.cell(i, 1).text = str(value)
        
        apply_table_styles(table)
    except Exception as e:
        logging.error(f"Error creating fund fundamentals slide: {str(e)}")

    #--- 3 --- Investment Team Slide ---
    try:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        title = slide.shapes.title
        title.text = "Investment Team"
        
        rows = len(investment_team) + 1
        cols = 4
        table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table
        
        headers = ["Name", "Title", "Join Year", "Background"]
        for i, header in enumerate(headers):
            table.cell(0, i).text = header
            
        for i, member in enumerate(investment_team, 1):
            table.cell(i, 0).text = member["name"]
            table.cell(i, 1).text = member["title"]
            table.cell(i, 2).text = str(member["join_date"]) if member["join_date"] else "N/A"
            table.cell(i, 3).text = member["background"]
        
        apply_table_styles(table)
    except Exception as e:
        logging.error(f"Error creating investment team slide: {str(e)}")

    #--- 4 --- Fees and Key Terms Slide ---
    try:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        title = slide.shapes.title
        title.text = "Fees and Key Terms"
        
        terms_data = fees_key_terms[0]
        
        rows = len(terms_data) + 1
        cols = 2
        table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table
        
        headers = ["Term", "Description"]
        for i, header in enumerate(headers):
            table.cell(0, i).text = header
            
        for i, (term, desc) in enumerate(terms_data.items(), 1):
            if term not in ['source', 'source_notes']:
                table.cell(i, 0).text = term.replace('_', ' ').title()
                table.cell(i, 1).text = str(desc)
        
        apply_table_styles(table)
    except Exception as e:
        logging.error(f"Error creating fees and key terms slide: {str(e)}")

    #--- 5 --- Deal History Slide ---
    try:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        title = slide.shapes.title
        title.text = "Deal History"
        
        rows = len(deal_history) + 1
        cols = 4
        table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table
        
        headers = ["Company", "Investment Date", "Exit Date", "Multiple"]
        for i, header in enumerate(headers):
            table.cell(0, i).text = header
            
        for i, deal in enumerate(deal_history, 1):
            table.cell(i, 0).text = deal["company"]
            table.cell(i, 1).text = deal["investment_date"]
            table.cell(i, 2).text = deal["exit_date"] if deal["exit_date"] else "Active"
            table.cell(i, 3).text = f"{deal['multiple']}x" if deal["multiple"] else "N/A"
        
        apply_table_styles(table)
    except Exception as e:
        logging.error(f"Error creating deal history slide: {str(e)}")

    #--- 6 --- Service Providers Slide ---
    try:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        title = slide.shapes.title
        title.text = "Service Providers"
        
        rows = len(service_providers) + 1
        cols = 2
        table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table
        
        headers = ["Role", "Provider"]
        for i, header in enumerate(headers):
            table.cell(0, i).text = header
            
        for i, provider in enumerate(service_providers, 1):
            table.cell(i, 0).text = provider["role"]
            table.cell(i, 1).text = provider["name"]
        
        apply_table_styles(table)
    except Exception as e:
        logging.error(f"Error creating service providers slide: {str(e)}")

    # Save to bytes
    try:
        ppt_bytes = BytesIO()
        prs.save(ppt_bytes)
        ppt_bytes.seek(0)
        return ppt_bytes.getvalue()
    except Exception as e:
        logging.error(f"Error saving PowerPoint to bytes: {str(e)}")
        raise

if __name__ == "__main__":
    generate_fund_analysis_ppt()