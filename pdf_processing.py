import pdfplumber
import tiktoken
import logging
from typing import List
from config import MAX_TOKENS_PER_CALL, OPENAI_MODEL

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
def extract_pdf_pages(pdf_path):
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
        print(f"Error extracting text from PDF: {e}")
        return None

#Function to get the token count for each pdf page
def get_page_token_counts(pdf_path: str) -> List[int]:
    """
    Returns a list of token counts for each page in the PDF.
    
    Parameters:
    pdf_path (str): Path to the PDF file.
    
    Returns:
    List[int]: A list of integers where each integer is the token count for a page.
    """
    # Extract the text for each page in the PDF
    pages = extract_pdf_pages(pdf_path)  # List of page texts
    page_token_counts = []

    # Count tokens for each page and store in the list
    for page in pages:
        token_count = count_tokens(page)  # Use your tokenizer to count tokens
        page_token_counts.append(token_count)

    return page_token_counts


def get_pdf_content_by_page_indices(pdf_path, start_page, end_page):
    # Extract all pages from the PDF as a list of text strings
    all_pages = extract_pdf_pages(pdf_path)
    
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
