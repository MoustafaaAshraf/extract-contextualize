"""
Medical Entity Extraction Package

This package provides tools for extracting medical entities from PDF documents.

Modules:
    extractor: Contains the Extractor class for medical entity extraction
    pdf_parser: Contains the PDFParser class for PDF text extraction
"""

from .extractor import Extractor
from .pdf_parser import PDFParser

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = ["Extractor", "PDFParser"]
