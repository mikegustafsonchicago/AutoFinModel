import os
import pdfplumber
import tiktoken
import logging
from typing import List
from config import MAX_TOKENS_PER_CALL, OPENAI_MODEL
from file_manager import get_project_uploads_path
from context_manager import get_user_context

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Function to count tokens for a given text
def count_tokens(text, model=OPENAI_MODEL):
    if text:
        tokenizer = tiktoken.encoding_for_model(model)
        tokens = tokenizer.encode(text)
        return len(tokens)
    else:
        logging.debug("Warning: No Text sent to count_tokens")
        return 0

# Function to extract text from a PDF, divided by pages
def extract_pdf_pages(file_name) -> List[str]:
    """
    Extracts text from each page of a PDF file.
    
    Parameters:
    file_name: The name of the PDF file
    
    Returns:
    List[str]: A list of strings where each string is the text content of a page.
    """
    user_context = get_user_context()
    # Get the full path to the PDF file
    uploads_dir = get_project_uploads_path()
    if not uploads_dir:
        logging.error(f"Could not find uploads directory for user {user_context.username} and project {user_context.current_project}")
        return []
        
    pdf_path = os.path.join(uploads_dir, file_name)
    if not os.path.exists(pdf_path):
        logging.error(f"PDF file not found: {pdf_path}")
        return []

    logging.debug(f"The pdf path is {pdf_path}")
    try:
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            # Loop through all pages and store text
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)
        return pages
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return []

#Function to get the token count for each pdf page
def get_page_token_counts(file_name) -> List[int]:
    """
    Returns a list of token counts for each page in the PDF.
    
    Parameters:
    file_name: The name of the PDF file
    Returns:
    List[int]: A list of integers where each integer is the token count for a page.
    """
    user_context = get_user_context()
    # Get the full path to the PDF file
    uploads_dir = get_project_uploads_path()
    if not uploads_dir:
        logging.error(f"Could not find uploads directory for user {user_context.username} and project {user_context.current_project}")
        return []
        
    pdf_path = os.path.join(uploads_dir, file_name)
    if not os.path.exists(pdf_path):
        logging.error(f"PDF file not found: {pdf_path}")
        return []
    
    # Extract the text for each page in the PDF
    pages = extract_pdf_pages(file_name)  # List of page texts
    page_token_counts = []

    # Count tokens for each page and store in the list
    for page in pages:
        token_count = count_tokens(page)  # Use your tokenizer to count tokens
        page_token_counts.append(token_count)

    return page_token_counts


def get_pdf_content_by_page_indices(file_name, start_page: int, end_page: int) -> str:
    """
    Returns the content of specified pages from a PDF file.
    
    Parameters:
    file_name: The name of the PDF file
    start_page (int): Starting page index
    end_page (int): Ending page index
    
    Returns:
    str: Combined text content of the specified pages with page boundary markers
    """
    user_context = get_user_context()
    # Get the full path to the PDF file
    uploads_dir = get_project_uploads_path()
    if not uploads_dir:
        logging.error(f"Could not find uploads directory for user {user_context.username} and project {user_context.current_project}")
        return ""
        
    pdf_path = os.path.join(uploads_dir, file_name)
    if not os.path.exists(pdf_path):
        logging.error(f"PDF file not found: {pdf_path}")
        return ""

    # Extract all pages from the PDF as a list of text strings
    all_pages = extract_pdf_pages(file_name)
    if not all_pages:
        return ""
    
    # Collect text for specified pages only
    selected_content = []
    for page_index in range(start_page, end_page):
        # Check if page index is within bounds
        if page_index < len(all_pages):
            page_text = all_pages[page_index]
            selected_content.append(page_text)
            # Append page boundary marker
            selected_content.append(f"---END OF PAGE {page_index + 1}---")
    
    # Join the selected page content with boundaries
    return "\n".join(selected_content)
