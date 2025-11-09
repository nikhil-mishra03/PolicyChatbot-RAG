from io import BytesIO
from typing import BinaryIO
from striprtf.striprtf import rtf_to_text
from pypdf import PdfReader

SUPPORTED_FILE_TYPES = ['application/pdf', 'text/plain', 'application/rtf']

def extract_text(
        *,
        file_stream: BinaryIO,
        filename: str,
        content_type: str 
) -> str:
    if content_type not in SUPPORTED_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {content_type} for text extraction. Supported types are: {SUPPORTED_FILE_TYPES}")
    
    data = file_stream.read()
    if not data:
        raise ValueError(f"No data found in file: {filename}")
    
    if content_type == 'application/pdf':
        return extract_pdf_text(data)
    
    if content_type == 'text/plain':
        return data.decode('utf-8')
    
    if content_type == 'application/rtf':
        return extract_rtf_text(data)
    
def extract_rtf_text(data: bytes) -> str:
    rtf_content = data.decode('utf-8', errors='ignore')
    text = rtf_to_text(rtf_content)
    if not text:
        raise ValueError("No text extracted from RTF document")
    return text

    
def extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    
    if not text:
        raise ValueError("No text extracted from PDF document.")
    
    return "\n".join(text)