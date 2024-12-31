import pytest
from pathlib import Path
from src.pdf_parser import PDFParser
import pdfplumber

@pytest.fixture
def pdf_parser():
    return PDFParser()

@pytest.fixture
def test_files_dir():
    return Path(__file__).parent / "test_files"

def test_parse_empty_pdf(pdf_parser, test_files_dir):
    result = pdf_parser.parse_pdf(test_files_dir / "empty.pdf")
    assert result == ""

def test_parse_simple_pdf(pdf_parser, test_files_dir):
    result = pdf_parser.parse_pdf(test_files_dir / "valid.pdf")
    assert "medical marvel" in result

def test_parse_corrupt_pdf(pdf_parser, test_files_dir):
    with pytest.raises(ValueError):
        pdf_parser.parse_pdf(test_files_dir / "corrupt.pdf")

def test_parse_nonexistent_pdf(pdf_parser):
    with pytest.raises(ValueError):
        pdf_parser.parse_pdf("nonexistent.pdf") 