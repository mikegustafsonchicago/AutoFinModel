# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 13:00:59 2024

@author: mikeg

This module handles PowerPoint presentation generation for real estate property analysis.
It creates slides showing property details, zoning information, and financial metrics.

Key components:
- Utility functions for styling and color handling 
- Main presentation generation function
- Individual slide generation for property aspects
"""

#------------------------------------------------------------------------------
# Imports and Setup
#------------------------------------------------------------------------------
import os
import json
import logging
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.dml.color import MSO_THEME_COLOR
from pptx.enum.text import PP_ALIGN
from pptx.oxml import parse_xml
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

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
    
def load_text(filepath):
    """
    Load and read text file content.
    
    Args:
        filepath (str): Path to text file
    Returns:
        str: Content of text file
    """
    with open(filepath, 'r') as file:
        return file.read()


def apply_table_styles(table, header_font_size=14):
    """
    Apply consistent styling to PowerPoint table headers and cells.
    Uses template theme colors with orange header.
    
    Args:
        table: PowerPoint table object
        header_font_size (int): Font size for header row
    """
    # Apply basic table style
    table.style = 'Table Grid'
    
    # Style headers using theme colors
    for cell in table.rows[0].cells:
        cell.fill.solid()
        # Use theme color (accent2 is typically orange in most templates)
        cell.fill.fore_color.theme_color = MSO_THEME_COLOR.ACCENT_2
        paragraph = cell.text_frame.paragraphs[0]
        paragraph.font.bold = True
        paragraph.font.size = Pt(header_font_size)
        # Use theme color for text to ensure contrast
        paragraph.font.theme_color = MSO_THEME_COLOR.LIGHT_1  # Usually white
    
    # Style data cells with subtle alternating shading
    for i in range(1, len(table.rows)):
        for cell in table.rows[i].cells:
            cell.fill.solid()
            if i % 2 == 0:
                cell.fill.fore_color.rgb = RGBColor(255, 255, 255)  # White
            else:
                cell.fill.fore_color.rgb = RGBColor(250, 250, 250)  # Very light gray
            paragraph = cell.text_frame.paragraphs[0]
            paragraph.font.size = Pt(12)
            paragraph.font.color.rgb = RGBColor(51, 51, 51)  # Dark gray for better readability
        
        # Adjust column widths at table level
        table.columns[0].width = Inches(2)  # Make first column narrower
        table.columns[1].width = Inches(3)  # Make second column wider

def generate_template_diagnostics(template_path, output_dir):
    """
    Generate a diagnostic text file with details about the PowerPoint template.
    
    Args:
        template_path (str): Path to the PowerPoint template file
        output_dir (str): Directory to save the diagnostic output
    """
    try:
        # Load the template
        prs = Presentation(template_path)
        
        # Create diagnostic text
        diagnostic_text = []
        diagnostic_text.append(f"PowerPoint Template Diagnostics\n")
        diagnostic_text.append(f"Template: {os.path.basename(template_path)}\n")
        diagnostic_text.append("-" * 80 + "\n")
        
        # Analyze slide layouts
        diagnostic_text.append("\nSlide Layouts:")
        diagnostic_text.append("-" * 40)
        for idx, layout in enumerate(prs.slide_layouts):
            diagnostic_text.append(f"\nLayout {idx}:")
            
            # Get placeholders in layout
            placeholders = []
            for shape in layout.placeholders:
                ph_type = str(shape.placeholder_format.type) if shape.placeholder_format else "Unknown"
                placeholders.append(f"    - Placeholder: idx={shape.placeholder_format.idx}, "
                                 f"type={ph_type}, "
                                 f"name='{shape.name}'")
            
            if placeholders:
                diagnostic_text.append("  Placeholders:")
                diagnostic_text.extend(placeholders)
            else:
                diagnostic_text.append("  No placeholders found")
                
        # Write to file
        diagnostic_path = os.path.join(output_dir, "template_diagnostics.txt")
        with open(diagnostic_path, 'w') as f:
            f.write("\n".join(diagnostic_text))
            
        return diagnostic_path
        
    except Exception as e:
        logging.error(f"Error generating template diagnostics: {str(e)}")
        raise


def get_gallery_images(gallery_path):
    """
    Get list of image filenames from the gallery directory.
    
    Returns:
        list: List of image filenames in the gallery directory
    """
    try:
        # Get list of files in gallery directory
        image_files = []
        for filename in os.listdir(gallery_path):
            # Check if file is an image by extension
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_files.append(filename)
        
        return sorted(image_files)
        
    except Exception as e:
        logging.error(f"Error getting gallery images: {str(e)}")
        raise


def estimate_text_width(text, font_size, font_name='Calibri', bold=False):
    """
    Estimate the width of text in PowerPoint given font parameters.
    Returns width in points.
    
    Args:
        text (str): Text to measure
        font_size (int): Font size in points
        font_name (str): Font family name
        bold (bool): Whether text is bold
    
    Returns:
        float: Estimated width in points
    """
    # Average character widths as proportion of font size
    # These are approximate multipliers based on common fonts
    char_width_ratios = {
        'Calibri': {
            'normal': {
                'uppercase': 0.6,
                'lowercase': 0.5,
                'digits': 0.5,
                'spaces': 0.3
            },
            'bold': {
                'uppercase': 0.65,
                'lowercase': 0.55,
                'digits': 0.55,
                'spaces': 0.3
            }
        }
    }
    
    # Default to Calibri if font not in our ratio dictionary
    ratios = char_width_ratios.get(font_name, char_width_ratios['Calibri'])
    ratios = ratios['bold'] if bold else ratios['normal']
    
    width = 0
    for char in text:
        if char.isupper():
            width += ratios['uppercase']
        elif char.islower():
            width += ratios['lowercase']
        elif char.isdigit():
            width += ratios['digits']
        elif char.isspace():
            width += ratios['spaces']
        else:
            # For symbols and other characters, use average of upper and lowercase
            width += (ratios['uppercase'] + ratios['lowercase']) / 2
            
    return width * font_size


def analyze_template_dimensions(presentation):
    """
    Analyze template to find standard margins based on title and footer ribbon placement.
    Checks main master slide first, then layouts if needed.
    
    Args:
        presentation: PowerPoint presentation object
    Returns:
        dict: Contains key dimensions like title_height, footer_height, and usable_area
    """
    dimensions = {
        'slide_width': presentation.slide_width,
        'slide_height': presentation.slide_height,
        'title_height': None,
        'footer_height': None,
        'footer_top': None
    }
    
    # First check the main master slide
    main_master = presentation.slide_masters[0]  # The first slide master is the main one
    
    logging.info("Analyzing main master slide...")
    
    # Check placeholders on main master
    title_found = False
    footer_found = False
    
    for placeholder in main_master.placeholders:
        # Check for title placeholder
        if placeholder.placeholder_format.type == 1:  # 1 = Title
            dimensions['title_height'] = int(placeholder.height)
            dimensions['title_top'] = placeholder.top
            title_found = True
            logging.info(f"Found title in master: height={placeholder.height}, top={placeholder.top}")
        
        # Look for footer placeholder
        if (placeholder.top + placeholder.height) > (presentation.slide_height - Inches(1)):
            footer_top = placeholder.top
            footer_height = int(placeholder.height)
            footer_found = True
            logging.info(f"Found footer in master: height={placeholder.height}, top={placeholder.top}")
    
    # Check shapes in main master
    bottom_area = {
        'top': None,
        'height': None
    }
    
    bottom_threshold = presentation.slide_height - Inches(1.5)
    for shape in main_master.shapes:
        # Check if shape is in bottom area
        if shape.top > bottom_threshold:
            shape_bottom = shape.top + shape.height
            logging.info(f"Found bottom shape in master: top={shape.top}, height={shape.height}, type={type(shape)}")
            
            # Initialize or update bottom area bounds
            if bottom_area['top'] is None or shape.top < bottom_area['top']:
                bottom_area['top'] = shape.top
            
            if bottom_area['height'] is None or shape_bottom > (bottom_area['top'] + bottom_area['height']):
                bottom_area['height'] = shape_bottom - bottom_area['top']
    
    # If we didn't find what we need in the master, check layouts
    if not title_found or (not footer_found and bottom_area['top'] is None):
        logging.info("Required elements not found in master, checking layouts...")
        # [Previous layout checking code here]
        for layout in presentation.slide_layouts:
            for placeholder in layout.placeholders:
                if not title_found and placeholder.placeholder_format.type == 1:
                    dimensions['title_height'] = int(placeholder.height)
                    dimensions['title_top'] = placeholder.top
                    title_found = True
                
                if not footer_found and (placeholder.top + placeholder.height) > (presentation.slide_height - Inches(1)):
                    footer_top = placeholder.top
                    footer_height = int(placeholder.height)
                    footer_found = True
            
            # Check shapes in layout if we still need bottom area
            if bottom_area['top'] is None:
                for shape in layout.shapes:
                    if shape.top > bottom_threshold:
                        shape_bottom = shape.top + shape.height
                        if bottom_area['top'] is None or shape.top < bottom_area['top']:
                            bottom_area['top'] = shape.top
                        if bottom_area['height'] is None or shape_bottom > (bottom_area['top'] + bottom_area['height']):
                            bottom_area['height'] = shape_bottom - bottom_area['top']
    
    # Determine which measurement to use for footer area
    if bottom_area['top'] is not None and bottom_area['height'] is not None:
        logging.info(f"Using bottom area: top={bottom_area['top']}, height={bottom_area['height']}")
        # Use bottom area if it's higher up than footer placeholder
        if footer_found and bottom_area['top'] < footer_top:
            dimensions['footer_top'] = bottom_area['top']
            dimensions['footer_height'] = bottom_area['height']
        else:
            dimensions['footer_top'] = footer_top
            dimensions['footer_height'] = footer_height
    elif footer_found:
        logging.info("Using footer placeholder measurements")
        # Fall back to footer placeholder if no bottom shapes found
        dimensions['footer_top'] = footer_top
        dimensions['footer_height'] = footer_height
    else:
        raise ValueError("Could not find required template elements (title and footer/bottom area)")
    
    # Calculate usable content area
    if dimensions['title_height'] and dimensions['footer_height']:
        dimensions['content_top'] = int(dimensions['title_top'] + dimensions['title_height'])   
        dimensions['content_height'] = int(dimensions['footer_top'] - dimensions['content_top'])
        dimensions['content_width'] = presentation.slide_width
        
        # Add some helpful derived measurements
        dimensions['left_column_width'] = (dimensions['content_width'] / 2) - Inches(0.125)
        dimensions['right_column_width'] = dimensions['left_column_width']
        dimensions['column_spacing'] = Inches(0.25)
        
        logging.info("Final Template Analysis Results:")
        for key, value in dimensions.items():
            logging.info(f"{key}: {value}")
        
        return dimensions
    else:
        raise ValueError("Could not find required template elements (title and footer/bottom area)")


    
    


#------------------------------------------------------------------------------
# Main Presentation Generation
#------------------------------------------------------------------------------
def generate_ppt():

    title_image_name = "southcarolina-header.jpg"

    current_directory = os.getcwd()
    file_name = "property_presentation.pptx"
    data_path = "users/projects/commercial_real_estate"
    template_name = os.path.join(os.path.dirname(__file__), "hucks_template.pptx")
    output_path = os.path.join(current_directory, "outputs", file_name)
    data_path = os.path.join(current_directory, data_path)
    
    gallery_path = os.path.join(data_path, "gallery")
    gallery_images = get_gallery_images(gallery_path)
    gallery_running_index = 0
    
    # Load property data and firm data
    try:
        property_fundamentals = load_json(os.path.join(data_path, "property_fundamentals.json"))
        property_zoning = load_json(os.path.join(data_path, "property_zoning.json"))
        property_financials = load_json(os.path.join(data_path, "property_financials.json"))
        firm_data = load_json(os.path.join(os.path.dirname(__file__), "firm_data.json"))
    except Exception as e:
        print(f"Error loading property or firm data: {str(e)}")
        raise

    # Create PowerPoint presentation
    presentation = Presentation(template_name)
    
    # Store slide dimensions for reuse
    SLIDE_WIDTH = presentation.slide_width
    SLIDE_HEIGHT = presentation.slide_height

    # Analyze template dimensions once
    template_dims = analyze_template_dimensions(presentation)
    TITLE_HEIGHT = template_dims['title_height']
    FOOTER_HEIGHT = template_dims['footer_height']
    CONTENT_TOP = template_dims['content_top']
    CONTENT_HEIGHT = template_dims['content_height']
    CONTENT_WIDTH = template_dims['content_width']

    print(f"Template Dimensiions:\n Title Height: {TITLE_HEIGHT}, Footer Height: {FOOTER_HEIGHT}")
    
    #--------------------------------------------------------------------------
    # SLIDE 1: Title Slide
    #--------------------------------------------------------------------------
    # Use blank layout instead of title layout
    title_slide = presentation.slides.add_slide(presentation.slide_layouts[6])  # Usually layout 6 is blank
    
    # Add background image first
    img_path = os.path.join(gallery_path, title_image_name)
    left = Inches(0)
    top = Inches(0) 
    background = title_slide.shapes.add_picture(img_path, left, top, SLIDE_WIDTH, SLIDE_HEIGHT)
    
    # Add text boxes manually instead of using placeholders
    # Calculate text width first to center the box
    title_text = f"Investment Overview: {property_fundamentals['property_details']['address']}"
    text_width = estimate_text_width(title_text, Pt(44))
    text_width = int(max(text_width, Inches(4)))  # Minimum 4 inches
    
    # Calculate left position to center the text box
    left = (SLIDE_WIDTH - text_width) / 2
    title_box = title_slide.shapes.add_textbox(left, Inches(2), text_width, Inches(1.5))
    
    title_frame = title_box.text_frame
    title_para = title_frame.add_paragraph()
    title_para.text = title_text
    title_para.font.size = Pt(44)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(255, 255, 255)
    title_para.alignment = PP_ALIGN.CENTER  # Center align the text within the box
    
    # Add white outline
    title_box.line.color.rgb = RGBColor(255, 255, 255)
    title_box.line.width = Pt(2)
    
    line = title_box.line
    line.color.rgb = RGBColor(255, 255, 255)
    line.width = Pt(2)
    

    subtitle_box = title_slide.shapes.add_textbox(Inches(0.5), Inches(6), Inches(8), Inches(2))
    subtitle_frame = subtitle_box.text_frame
    subtitle_para = subtitle_frame.add_paragraph()
    subtitle_para.text = f"{property_fundamentals['property_details']['municipality']}\n\n{firm_data['firm_details']['name']}\n{firm_data['firm_details']['contacts'][0]['email']}"
    subtitle_para.font.size = Pt(14)
    subtitle_para.font.color.rgb = RGBColor(255, 255, 255)
    



    #--------------------------------------------------------------------------
    # SLIDE 2: Property Fundamentals
    #--------------------------------------------------------------------------
    slide = presentation.slides.add_slide(presentation.slide_layouts[10])
    title = slide.shapes.title
    title.text = "Property Highlights"
    
    fund_details = property_fundamentals['property_details']
    rows = len(fund_details) + 1
    cols = 2
    
    # Calculate table and image widths based on split ratio (e.g. 40% table, 60% image)
    table_width_ratio = 0.4  # Adjust this value to change the split
    image_width_ratio = 1 - table_width_ratio
    
    table_width = int(SLIDE_WIDTH * table_width_ratio - Inches(0.25))  # Subtract margin
    
    # Create table with new width
    table = slide.shapes.add_table(rows, cols, Inches(0.125), Inches(1.5),
                                 table_width, Inches(4.00)).table

    # Merge header cells and set text
    table.cell(0, 0).merge(table.cell(0, 1))
    table.cell(0, 0).text = "Overview"

    row = 1
    for key, value in fund_details.items():
        # Set white background for each row
        for col in range(cols):
            cell = table.cell(row, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(255, 255, 255)
        
        table.cell(row, 0).text = key.replace('_', ' ').title()
        table.cell(row, 1).text = str(value)
        row += 1

    apply_table_styles(table)

    # Add gallery image to right side of slide
    if gallery_images[gallery_running_index]:
        selected_image = os.path.join(gallery_path, gallery_images[gallery_running_index])
        # Get image dimensions before adding to slide
        with Image.open(selected_image) as img:
            img_width, img_height = img.size
            # Calculate aspect ratio
            aspect_ratio = img_width / img_height
        
        # Calculate image position and size based on ratio
        left_x = int(SLIDE_WIDTH * table_width_ratio + Inches(0.125))  # Add margin
        image_width = int(SLIDE_WIDTH * image_width_ratio - Inches(0.25))  # Subtract margin
        image_height = image_width / aspect_ratio
        
        # Center image vertically
        top_y = TITLE_HEIGHT + ((SLIDE_HEIGHT - TITLE_HEIGHT - FOOTER_HEIGHT - image_height) / 2)
       
        # Add image
        image = slide.shapes.add_picture(selected_image, left_x, top_y,
                                       image_width, image_height)
        gallery_running_index += 1

    #--------------------------------------------------------------------------
    # SLIDE 3: Zoning & Financial Details
    #--------------------------------------------------------------------------
    slide = presentation.slides.add_slide(presentation.slide_layouts[10])
    title = slide.shapes.title
    title.text = "Zoning & Financial Details"
    
    # Left table - Zoning details
    zoning_details = property_zoning['property_details']
    rows = len(zoning_details) + 1
    cols = 2

    width = int((SLIDE_WIDTH/2)*.8)  
    left_x = int(((SLIDE_WIDTH/2) - width)/2)  
    top_y = Inches(1.5)
    height = Inches(4.00)
    left_table = slide.shapes.add_table(rows, cols, left_x, top_y, width, height).table
    print(f"Left Table Dimensions: Left: {left_x}, Top: {top_y}, Width: {width}, Height: {height}, slide width: {SLIDE_WIDTH}")

    # Merge header cells and set text
    left_table.cell(0, 0).merge(left_table.cell(0, 1))
    left_table.cell(0, 0).text = "Zoning Overview"

    row = 1
    for key, value in zoning_details.items():
        left_table.cell(row, 0).text = key.replace('_', ' ').title()
        left_table.cell(row, 1).text = str(value)
        row += 1

    apply_table_styles(left_table)

    # Right table - Financial details
    financial_details = property_financials['property_details']
    rows = len(financial_details) + 1
    cols = 2
    width = int((SLIDE_WIDTH/2)*.8) 
    left_x = int(((SLIDE_WIDTH/2) - width)/2+SLIDE_WIDTH/2)
    right_table = slide.shapes.add_table(rows, cols, left_x, top_y, width, height).table
    print(f"Right Table Dimensions: Left: {left_x}, Top: {top_y}, Width: {width}, Height: {height}, slide width: {SLIDE_WIDTH}")

    # Merge header cells and set text
    right_table.cell(0, 0).merge(right_table.cell(0, 1))
    right_table.cell(0, 0).text = "Financial Overview"

    row = 1
    for key, value in financial_details.items():
        right_table.cell(row, 0).text = key.replace('_', ' ').title()
        right_table.cell(row, 1).text = str(value)
        row += 1

    apply_table_styles(right_table)

   

    #--------------------------------------------------------------------------
    # Photo Gallery Slides
    #--------------------------------------------------------------------------
    # Get list of images from gallery folder
 
    if os.path.exists(gallery_path):
        image_files = [f for f in os.listdir(gallery_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        
        for image_file in image_files:
            if image_file == title_image_name:
                continue
            # Add new slide for each image
            slide = presentation.slides.add_slide(presentation.slide_layouts[10])  # Blank layout
            
            # Add title
            title = slide.shapes.title
            title.text = "Property View"
            
            # Calculate dimensions to maintain aspect ratio while fitting in slide
            img_path = os.path.join(gallery_path, image_file)
            
            # Center the image horizontally and vertically

            
            # Get original image dimensions
            with Image.open(img_path) as img:
                img_width, img_height = img.size
            
            # Calculate aspect ratio
            image_aspect_ratio = img_width / img_height
            full_area_ratio = SLIDE_WIDTH / (SLIDE_HEIGHT - TITLE_HEIGHT)

            print(f" Image Name: {image_file}")
            print(f" Image Aspect Ratio: {round(image_aspect_ratio, 2)}")
            print(f" Full Aspect Ratio: {round(full_area_ratio, 2)}")
            print(f" Delta: {round(abs(image_aspect_ratio - full_area_ratio), 2)}")
            print(f" SLIDE_HEIGHT: {SLIDE_HEIGHT}, TITLE_HEIGHT: {TITLE_HEIGHT}, FOOTER_HEIGHT: {FOOTER_HEIGHT}")
            print("\n")
            
            # Set max dimensions while preserving aspect ratio
            max_width = SLIDE_WIDTH
            max_height = SLIDE_HEIGHT - TITLE_HEIGHT
            
            # First, check if image aspect ratio is suitable for the full slide area below title
            # This area includes the footer ribbon, which is fine if we want to cover it
            ratio_difference = abs(image_aspect_ratio - full_area_ratio)
            
            if ratio_difference < 0.45:
                # Image ratio is close enough to full area ratio (within 40%)
                # We'll stretch/compress slightly to fill the full area
                # This is acceptable since the difference is small
                width = max_width
                height = max_height
            else:
                # Image ratio differs too much from full area ratio
                # Now we'll fit it in the content area between title and footer
                content_area_ratio = CONTENT_WIDTH / (CONTENT_HEIGHT)
                
                if image_aspect_ratio > content_area_ratio:
                    # Image is wider than content area
                    # Use full width and calculate proportional height
                    width = max_width
                    height = round(width / image_aspect_ratio)
                else:
                    # Image is taller than content area
                    # Use available height (excluding footer) and calculate proportional width
                    height = CONTENT_HEIGHT
                    width = round(height * image_aspect_ratio)
            # Calculate centered position
            left = int((SLIDE_WIDTH - width) / 2)
            top_y = CONTENT_TOP
            
            # Add the image
            slide.shapes.add_picture(img_path, left, top_y, width, height)

    #--------------------------------------------------------------------------
    # SLIDE Last-1: About Us
    #--------------------------------------------------------------------------
    slide = presentation.slides.add_slide(presentation.slide_layouts[10])
    title = slide.shapes.title
    title.text = "About Us"

    # Add firm details from firm_data.json
    firm_details = firm_data['firm_details']
    
    # Add text box for firm details
    text_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5))
    text_frame = text_box.text_frame
    text_frame.word_wrap = True
    
    # Add company description
    p = text_frame.add_paragraph()
    p.text = firm_details['about']
    p.font.size = Pt(11)
    p.font.name = 'Calibri'
    p.space_after = Pt(12)
    
    # Add contact information
    p = text_frame.add_paragraph()
    p.text = f"Address: {firm_details['address']}"
    p.font.size = Pt(10)
    p.font.name = 'Calibri'
    
    p = text_frame.add_paragraph()
    p.text = f"Website: {firm_details['website']}"
    p.font.size = Pt(10)
    p.font.name = 'Calibri'
    p.space_after = Pt(12)
    
    # Add team contacts
    for contact in firm_details['contacts']:
        p = text_frame.add_paragraph()
        p.text = f"{contact['name']} - {contact['title']}"
        p.font.size = Pt(10)
        p.font.name = 'Calibri'
        
        p = text_frame.add_paragraph()
        p.text = f"Phone: {contact['phone']} | Email: {contact['email']}"
        p.font.size = Pt(10)
        p.font.name = 'Calibri'
        p.space_after = Pt(8)

    #--------------------------------------------------------------------------
    # SLIDE Last: Legal Disclaimer
    #--------------------------------------------------------------------------
    slide = presentation.slides.add_slide(presentation.slide_layouts[11])
    '''
    title = slide.shapes.title
    title.text = "Legal Disclaimer"

    # Load about us text
    about_us_path = os.path.join(os.path.dirname(__file__), "disclaimer.txt")
    with open(about_us_path, 'r') as f:
        about_us_text = f.read()

    # Add text box for about us content
    text_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5))
    text_frame = text_box.text_frame
    text_frame.word_wrap = True

    # Format text by splitting into paragraphs and applying consistent formatting
    text_frame.clear()  # Clear existing text
    paragraphs = about_us_text.split('\n\n')  # Split on double newlines
    
    for text in paragraphs:
        if text.strip():  # Only process non-empty paragraphs
            p = text_frame.add_paragraph()
            p.text = text.strip()
            p.font.size = Pt(10)
            p.font.name = 'Calibri'
            p.space_after = Pt(12)  # Add spacing between paragraphs
'''
    # Add theme colors slide
    add_diagnostics_slide(presentation)

    # Generate template diagnostics
    generate_template_diagnostics(template_name, os.path.dirname(output_path))

    # Save PowerPoint
    presentation.save(output_path)
    print(f"Presentation saved to {output_path}")

def add_diagnostics_slide(presentation):
    """
    Add a slide showing template dimensions and theme colors.
    
    Args:
        presentation: PowerPoint presentation object
    """
    # Create a slide to show dimensions and colors
    slide = presentation.slides.add_slide(presentation.slide_layouts[10])
    title = slide.shapes.title
    title.text = "Template Dimensions & Colors"
    
    # Get template dimensions
    dims = analyze_template_dimensions(presentation)
    
    # Add dimension visualization shapes
    # Title area
    title_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 
        Inches(1), dims['title_top'], Inches(2), dims['title_height'])
    title_box.fill.solid()
    title_box.fill.fore_color.rgb = RGBColor(200, 200, 200)
    title_box.line.color.rgb = RGBColor(100, 100, 100)
    
    # Add text to title box
    title_text = title_box.text_frame
    title_text.text = f"Title Area\nHeight: {dims['title_height']/914400:.2f}\"\nTop: {dims['title_top']/914400:.2f}\" (title_top)"
    title_text.paragraphs[0].font.size = Pt(8)
    title_text.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
    title_text.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # Content area
    content_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(1), dims['content_top'], Inches(2), dims['content_height'])
    content_box.fill.solid() 
    content_box.fill.fore_color.rgb = RGBColor(230, 230, 230)
    content_box.line.color.rgb = RGBColor(100, 100, 100)
    
    # Add text to content box
    content_text = content_box.text_frame
    content_text.text = f"Content Area\nHeight: {dims['content_height']/914400:.2f}\"\nTop: {dims['content_top']/914400:.2f}\" (content_top)"
    content_text.paragraphs[0].font.size = Pt(8)
    content_text.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
    content_text.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # Footer area
    footer_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(1), dims['footer_top'], Inches(2), dims['footer_height'])
    footer_box.fill.solid()
    footer_box.fill.fore_color.rgb = RGBColor(200, 200, 200)
    footer_box.line.color.rgb = RGBColor(100, 100, 100)
    
    # Add text to footer box
    footer_text = footer_box.text_frame
    footer_text.text = f"Footer Area\nHeight: {dims['footer_height']/914400:.2f}\"\nTop: {dims['footer_top']/914400:.2f}\" (footer_top)"
    footer_text.paragraphs[0].font.size = Pt(10)
    footer_text.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
    footer_text.paragraphs[0].alignment = PP_ALIGN.CENTER
    footer_text.paragraphs[1].font.size = Pt(10)
    footer_text.paragraphs[1].font.color.rgb = RGBColor(0, 0, 0)
    footer_text.paragraphs[1].alignment = PP_ALIGN.CENTER
    
    # Add dimension labels
    labels = {
        'Title Height': dims['title_height'],
        'Content Top': dims['content_top'],
        'Content Height': dims['content_height'],
        'Footer Height': dims['footer_height'],
        'Footer Top': dims['footer_top'],
        'Slide Width': presentation.slide_width,
        'Slide Height': presentation.slide_height
    }
    
    # Add labels with measurements
    for i, (label, value) in enumerate(labels.items()):
        text = slide.shapes.add_textbox(Inches(4), Inches(1.5 + i*0.4), Inches(4), Inches(0.3))
        text.text_frame.text = f"{label}: {value/914400:.2f} inches"  # Convert EMU to inches
        
    # Add theme colors in compact form
    theme_colors = {
        'ACCENT_1': MSO_THEME_COLOR.ACCENT_1,
        'ACCENT_2': MSO_THEME_COLOR.ACCENT_2,
        'DARK_1': MSO_THEME_COLOR.DARK_1,
        'LIGHT_1': MSO_THEME_COLOR.LIGHT_1,
    }
    
    for i, (name, color) in enumerate(theme_colors.items()):
        shape = slide.shapes.add_textbox(Inches(4), Inches(5 + i*0.3), Inches(4), Inches(0.3))
        paragraph = shape.text_frame.paragraphs[0]
        paragraph.text = f"Color: {name}"
        paragraph.font.theme_color = color

if __name__ == "__main__":
    generate_ppt()