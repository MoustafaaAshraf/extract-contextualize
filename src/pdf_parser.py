import pdfplumber
from typing import List

# TODO: Document better

def parse_pdf(file_path: str) -> str:
    """
    Parse the PDF file and return the extracted text as a single string.
    """
    all_text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
    return "\n".join(all_text)
