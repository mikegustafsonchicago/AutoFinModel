import os
import pdfplumber
import tiktoken
import logging
from typing import List
from config import MAX_TOKENS_PER_CALL, OPENAI_MODEL, BUCKET_NAME
from file_manager import get_project_uploads_path
from context_manager import get_user_context
from upload_file_manager import count_tokens
from boto3 import client
from botocore.exceptions import ClientError
import tempfile

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize S3 client
s3_client = client('s3')



# Function to extract text from a PDF, divided by pages
def extract_pdf_pages(file_name) -> List[str]:
    """
    Extracts text from each page of a PDF file in S3.
    
    Parameters:
    file_name: The name of the PDF file
    
    Returns:
    List[str]: A list of strings where each string is the text content of a page.
    """
    user_context = get_user_context()
    uploads_dir = get_project_uploads_path()
    if not uploads_dir:
        logging.error(f"Could not find uploads directory for user {user_context.username}")
        return []
        
    pdf_path = f"{uploads_dir}/{file_name}".replace('\\', '/')
    
    try:
        # Create temp file that deletes itself when closed
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as temp_file:
            # Download PDF from S3
            s3_client.download_file(BUCKET_NAME, pdf_path, temp_file.name)
            
            # Process PDF while temp file is still open
            pages = []
            with pdfplumber.open(temp_file.name) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    pages.append(page_text)
            
            return pages
            
    except ClientError as e:
        logging.error(f"Error accessing PDF in S3: {e}")
        return []
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
    
    # Ensure consistent forward slashes for S3 paths
    pdf_path = f"{uploads_dir}/{file_name}".replace('\\', '/')
    
    # Check if file exists in S3 instead of local filesystem
    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=pdf_path)
    except ClientError:
        logging.error(f"PDF file not found in S3: {pdf_path}")
        return []
    
    # Extract the text for each page in the PDF
    pages = extract_pdf_pages(file_name)  # List of page texts
    
    page_token_counts = []

    # Count tokens for each page and store in the list
    for i, page in enumerate(pages):
        token_count = count_tokens(page)  # Use your tokenizer to count tokens
        page_token_counts.append(token_count)

    return page_token_counts


def get_pdf_content_by_page_indices(file_name, start_page: int, end_page: int) -> str:
    """
    Returns the content of specified pages from a PDF file in S3.
    
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
        
    # Ensure consistent forward slashes for S3 paths
    pdf_path = f"{uploads_dir}/{file_name}".replace('\\', '/')
    
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
