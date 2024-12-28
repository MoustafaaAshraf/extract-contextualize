import pytest
from fastapi.testclient import TestClient
from src.app import app
import os

# TODO: test a simple i/o
# TODO: test lower level functions

client = TestClient(app)

def test_extract_empty_file():
    # Test with no file
    response = client.post("/api/v1/extract")
    assert response.status_code == 422  # FastAPI's default error for missing required field

def test_extract_invalid_file():
    # Test with non-PDF file
    files = {'file': ('invalid.txt', b'Some text content', 'text/plain')}
    response = client.post("/api/v1/extract", files=files)
    assert response.status_code == 400

def test_extract_valid_pdf():
    # Create a test PDF file path
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'test_files', 'valid.pdf')
    
    # Skip if test file doesn't exist
    if not os.path.exists(test_pdf_path):
        pytest.skip("Test PDF file not found")
    
    with open(test_pdf_path, 'rb') as pdf_file:
        files = {'file': ('valid.pdf', pdf_file, 'application/pdf')}
        response = client.post("/api/v1/extract", files=files)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)