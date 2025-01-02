import os
import json
import logging
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor, MSO_THEME_COLOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN


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
